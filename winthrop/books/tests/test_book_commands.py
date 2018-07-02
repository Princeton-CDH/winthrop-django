import csv
from collections import defaultdict
from io import StringIO
from unittest.mock import patch
import os

from django.core.management import call_command
from django.test import TestCase
from djiffy.models import Manifest

from winthrop.books.models import Book, OwningInstitution
from winthrop.books.management.commands import import_nysl, import_digitaleds


FIXTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           '..', 'fixtures')


@patch('winthrop.people.models.Person.set_birth_death_years')  # skip viaf
class TestImportNysl(TestCase):

    test_csv = os.path.join(FIXTURE_DIR, 'test_nysl_data.csv')

    def setUp(self):
        self.cmd = import_nysl.Command()
        self.cmd.stdout = StringIO()
        # setup normally done in handle()
        self.cmd.stats = defaultdict(int)
        self.cmd.nysl = OwningInstitution.objects.get(short_name='NYSL')

        # Kludge to get dummy values in the command we're using to test for
        # API lookups, since we're already hacking it a bit.
        # TODO: Figure out how to mock this instead
        def dummy_viaf(*args, **kwargs):
            return 'http://totallyviaf.org/viaf/00001/'
        def dummy_geonames(*args, **kwargs):
            return {
                'latitude': 0,
                'longitude': 0,
                'geonames_id': 'http://notgeonames/0001/'
            }

        self.cmd.viaf_lookup = dummy_viaf
        self.cmd.geonames_lookup = dummy_geonames

    def test_run(self, mocksetbirthdeath):
            out = StringIO()
            # pass the modified self.cmd object
            call_command(self.cmd, self.test_csv, stdout=out)
            output = out.getvalue()
            assert 'Imported content' in output
            assert '4 books' in output # Duplicated book to test expected behavior
            assert '3 places' in output
            assert '3 people' in output
            assert '3 publishers' in output

    def test_create_book(self, mocksetbirthdeath):
        # load data from fixture to test book creation more directly
        # TODO: Update to account for new variations
        with open(self.test_csv) as csvfile:
            csvreader = csv.DictReader(csvfile)
            de_christelicke = next(csvreader)
            mercurii = next(csvreader)
            opera = next(csvreader)

        # test against first row of fixture data
        data = de_christelicke
        # Cleanup for exact fields that will need it to match expected
        for key, value in data.items():
            if key and key.endswith('itle'):
                data[key] = value.strip('. ')

        self.cmd.create_book(data)
        # find book object by short title and compare data
        book = Book.objects.get(short_title=data['Short Title'])
        assert book.title == data['Title']
        assert book.pub_year == int(data['Year of Publication'])
        assert book.is_extant
        assert book.original_pub_info == data['PUB INFO - Original']
        assert not book.is_annotated
        ## Account for notes on the flagged for reproduction
        assert book.notes == data['Notes']
        # test fields on related models
        assert book.pub_place.name == data['Modern Place of Publication']
        # Is geonames_id getting set and passed from call?
        assert book.pub_place.geonames_id == 'http://notgeonames/0001/'
        assert book.publisher.name == data['Standardized Name of Publisher']
        # - first row has author, no editor or translator
        assert book.authors().first().person.authorized_name == \
            data['AUTHOR, Standarized']
        # Is viaf_id getting set and passed from call?
        assert book.authors().first().person.viaf_id == \
            'http://totallyviaf.org/viaf/00001/'
        book_creators = book.creator_set.all()
        assert book_creators.filter(creator_type__name='Editor').count() == 0
        assert book_creators.filter(creator_type__name='Translator').count() == 0
        # check that NYSL cataloguing information created correctly
        nysl_catalogue = book.catalogue_set.get(institution__short_name='NYSL')
        assert nysl_catalogue.call_number == data['NYSL CALL NUMBER']
        assert nysl_catalogue.is_current
        assert nysl_catalogue.notes == data['NYSL -- NOTES']

        # test variations in second row of fixture data
        data = mercurii
        # cleanup for exact fields that needed it
        for key, value in data.items():
            if key and key.endswith('itle'):
                data[key] = value.strip('. ')

        self.cmd.create_book(data)
        # find book object by short title and compare data
        book = Book.objects.get(short_title=data['Short Title'])
        assert book.red_catalog_number == data['RED catalogue number at the front']
        # ink and pencil are 'NA' in fixture; should be empty
        assert book.ink_catalog_number == ''
        assert book.pencil_catalog_number == ''

        # test for expected short title when building short title
        # Also check for the annotated field import
        data = opera

        # Handle cleanup for exact fields that needed it
        for key, value in data.items():
            if key and key.endswith('itle'):
                data[key] = value.strip('. ')

        self.cmd.create_book(data)
        short_title = ' '.join((data['Title'].split())[0:3])
        # Find the book by short title
        book = Book.objects.get(short_title=short_title)
        assert book.short_title == short_title
        # Test that the reproduction notes were pulled as expected
        assert book.notes == data['Notes'] + \
            '\n\nReproduction Recommendation: Front flyleaf recto, TP'
        # Check that is_sammelband was set on a 'bound' volume
        self.cmd.create_book(data)
        self.cmd.build_sammelband()
        assert book.catalogue_set.first().is_sammelband == True


class TestWinthropManifestImporter(TestCase):
    fixtures = ['sample_book_data.json']

    def setUp(self):
        self.importer = import_digitaleds.WinthropManifestImporter()

    @patch('winthrop.books.management.commands.import_digitaleds.ManifestImporter.import_manifest')
    @patch('winthrop.books.management.commands.import_digitaleds.ManifestImporter.error_msg')
    def test_matching(self, mockerror_msg, mocksuperimport):
        manifest_uri = 'http://so.me/manifest/uri'
        path = '/path/to/manifest.json'

        # simulate import failed
        mocksuperimport.return_value = None

        assert self.importer.import_manifest(manifest_uri, path) == None
        mocksuperimport.assert_called_with(manifest_uri, path)

        # simulate import success but not local identifier
        db_manif = Manifest(label='Test Manifest', short_id='123ab')
        # NOTE: using unsaved db manifest object to avoid import skipping
        # due to manifest uri already being in the database
        mocksuperimport.return_value = db_manif
        assert self.importer.import_manifest(manifest_uri, path) == db_manif
        mockerror_msg.assert_called_with('No local identifier found')

        # local identifier but no match in local book db
        db_manif.metadata = {'Local identifier': ['Win 100']}
        self.importer.import_manifest(manifest_uri, path)
        mockerror_msg.assert_called_with('No match for Win 100')

        # local identifier matches book in fixture
        db_manif.metadata['Local identifier'] = ['Win 60']
        # must be saved in the db to link to book record
        db_manif.save()
        self.importer.import_manifest(manifest_uri, path)
        book = Book.objects.get(catalogue__call_number='Win 60')
        assert book.digital_edition == db_manif


@patch('winthrop.books.management.commands.import_digitaleds.WinthropManifestImporter')
class TestImportDigitalEds(TestCase):

    def test_command(self, mockimporter):
        cmd = import_digitaleds.Command()

        # normal file/uri
        test_paths = ['one', 'two']
        cmd.handle(path=test_paths)
        assert mockimporter.return_value.import_paths.called_with(test_paths)

        # shortcut for nysl
        cmd.handle(path=['NYSL'])
        assert mockimporter.return_value.import_paths \
            .called_with([cmd.manifest_uris['NYSL']])

        # works within a list also
        cmd.handle(path=['one', 'NYSL', 'two'])
        assert mockimporter.return_value.import_paths \
            .called_with(['one', cmd.manifest_uris['NYSL'], 'two'])
