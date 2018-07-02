from collections import defaultdict
import csv
from datetime import datetime
from io import StringIO
import json
from time import sleep
from unittest.mock import patch, Mock
import os

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db.models.query import QuerySet
from django.utils.safestring import mark_safe
from django.test import TestCase
from django.urls import reverse
from djiffy.models import Manifest
import pytest

from winthrop.common.solr import Indexable, PagedSolrQuery
from winthrop.places.models import Place
from winthrop.people.models import Person
from .models import OwningInstitution, Book, Publisher, Catalogue, \
    Creator, CreatorType, Subject, BookSubject, Language, BookLanguage, \
    PersonBook, PersonBookRelationshipType
from .management.commands import import_nysl, import_digitaleds


FIXTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
    'fixtures')


class TestOwningInstitution(TestCase):
    fixtures = ['sample_book_data.json']

    def test_str(self):
        long_name = 'New York Society Library'
        short_name = 'NYSL'
        inst = OwningInstitution(name=long_name)
        # should use long name if no short name is set
        assert str(inst) == long_name
        inst.short_name = short_name
        assert str(inst) == short_name

    def test_book_count(self):
        # test abstract book count mix-in via owning institution model
        # tests that html for admin form is rendered correctly

        pl = Place.objects.first()
        inst = OwningInstitution.objects.create(name='NYSL',
            place=pl)
        # new institution has no books associated
        base_url = reverse('admin:books_book_changelist')
        assert inst.book_count() == \
            mark_safe('<a href="%s?%ss__id__exact=%s">%s</a>' %
                (base_url,
                inst.__class__.__name__.lower(),
                inst.pk,
                0)
            )

        # create a book and associated it with the institution
        pub = Publisher.objects.create(name='Pub Lee')
        bk = Book.objects.create(title='Some rambling long old title',
            short_title='Some rambling',
            original_pub_info='foo',
            publisher=pub, pub_place=pl, pub_year=1823,
            is_extant=False, is_annotated=False)

        cat = Catalogue.objects.create(institution=inst, book=bk,
            is_current=False, is_sammelband=False)


        assert inst.book_count() == \
            mark_safe('<a href="%s?%ss__id__exact=%s">%s</a>' %
                (base_url,
                inst.__class__.__name__.lower(),
                inst.pk,
                1)
            )


class TestBook(TestCase):
    fixtures = ['sample_book_data.json']

    def test_str(self):
        de_christelicke = Book.objects.get(short_title__contains="De Christelicke")

        assert '%s (%s)' % (de_christelicke.short_title, de_christelicke.pub_year) \
            == str(de_christelicke)

    def test_catalogue_call_numbers(self):
        de_christelicke = Book.objects.get(short_title__contains="De Christelicke")

        # fixture has one call number
        assert de_christelicke.catalogue_call_numbers() == 'Win 60'

        # add a second catalogue record
        owning_inst = OwningInstitution.objects.first()
        cat = Catalogue.objects.create(institution=owning_inst,
            book=de_christelicke, call_number='NY789', is_current=True)

        assert de_christelicke.catalogue_call_numbers() == 'Win 60, NY789'

    def test_authors(self):
        de_christelicke = Book.objects.get(short_title__contains="De Christelicke")

        laski = 'Łaski, Jan'
        assert de_christelicke.authors().count() == 1
        assert de_christelicke.authors().first().person.authorized_name == \
            laski
        assert de_christelicke.author_names() == laski

        # modify fixture data to test two authors
        abelin_jp = "Abelin, Johann Philipp"
        abelin = Person.objects.get(authorized_name=abelin_jp)
        creator_author = CreatorType.objects.get(name='Author')
        Creator.objects.create(creator_type=creator_author,
            person=abelin, book=de_christelicke)
        assert de_christelicke.authors().count() == 2

        assert de_christelicke.author_names() == '%s, %s' % (laski, abelin_jp)

        # and no authors
        de_christelicke.creator_set.all().delete()
        assert de_christelicke.authors().count() == 0

    def test_add_author(self):
        de_christelicke = Book.objects.get(short_title__contains="De Christelicke")
        abelin = Person.objects.get(authorized_name="Abelin, Johann Philipp")
        de_christelicke.add_author(abelin)
        # check that appropriate creator model was created
        assert Creator.objects.filter(creator_type__name='Author',
            person=abelin, book=de_christelicke).count() == 1
        assert de_christelicke.authors().count() == 2

    def test_add_editor(self):
        de_christelicke = Book.objects.get(short_title__contains="De Christelicke")
        abelin = Person.objects.get(authorized_name="Abelin, Johann Philipp")
        de_christelicke.add_editor(abelin)
        # check that appropriate creator model was created
        assert Creator.objects.filter(creator_type__name='Editor',
            person=abelin, book=de_christelicke).count() == 1

    def test_add_translator(self):
        de_christelicke = Book.objects.get(short_title__contains="De Christelicke")
        abelin = Person.objects.get(authorized_name="Abelin, Johann Philipp")
        de_christelicke.add_translator(abelin)
        # check that appropriate creator model was created
        assert Creator.objects.filter(creator_type__name='Translator',
            person=abelin, book=de_christelicke).count() == 1

    def test_is_digitized(self):
        # is digitized property based on digital edition
        de_christelicke = Book.objects.get(short_title__contains="De Christelicke")
        # no digital edition associated
        assert not de_christelicke.is_digitized()

        # add digital edition
        de_christelicke.digital_edition = Manifest.objects.first()
        assert de_christelicke.is_digitized()

    @patch.object(Indexable, 'index_items')
    def test_handle_person_save(self, mock_index_items):

        author = Person.objects.all().first()

        # only reindex on name change
        Book.handle_person_save(Mock(), author)
        # index not called because collection name has not changed
        mock_index_items.assert_not_called()

        # modify name to test indexing
        author.authorized_name = 'Another'
        book = Book.objects.filter(contributors=author).first()
        Book.handle_person_save(Mock(), author)
        # call must be inspected piecemeal because queryset equals comparison fails
        args, kwargs = mock_index_items.call_args
        assert isinstance(args[0], QuerySet)
        assert book in args[0]
        assert kwargs['params'] == {'commitWithin': 3000}

    @patch.object(Indexable, 'index_items')
    def test_handle_person_delete(self, mock_index_items):
        author = Person.objects.all().first()
        book = Book.objects.filter(contributors=author).first()

        Book.handle_person_delete(Mock(), author)

        assert author.book_set.count() == 0
        args, kwargs = mock_index_items.call_args
        assert isinstance(args[0], QuerySet)
        assert book in args[0]
        assert kwargs['params'] == {'commitWithin': 3000}

    def test_index_id(self):
        book = Book.objects.all().first()
        assert book.index_id() == 'book:%d' % book.pk

    def test_index_data(self):
        book = Book.objects.filter(digital_edition__isnull=True).first()
        # no digital edition associated
        index_data = book.index_data()
        assert index_data['content_type'] == 'books.book'
        assert index_data['id'] == book.index_id()
        assert index_data['title'] == book.title
        assert index_data['short_title'] == book.short_title
        for auth in book.authors():
            assert auth.person.authorized_name in index_data['authors']
        assert index_data['pub_year'] == book.pub_year
        assert not index_data['thumbnail']
        assert not index_data['thumbnail_label']
        assert index_data['author_exact'] == book.authors()[0].person.authorized_name

        # associate digital edition from fixture (has no thumbnail)
        book.digital_edition = Manifest.objects.first()
        # has digital edition but no thumbnail
        # book = Book.objects.filter(digital_edition__isnull=False).first()
        index_data = book.index_data()
        assert not index_data['thumbnail']
        assert not index_data['thumbnail_label']

        # mark canvas as thumbnail
        canvas = book.digital_edition.canvases.first()
        canvas.thumbnail = True
        canvas.save()
        index_data = book.index_data()
        assert index_data['thumbnail'] == canvas.iiif_image_id
        assert index_data['thumbnail_label'] == canvas.label

        # no authors
        book.creator_set.all().delete()
        index_data = book.index_data()
        assert index_data['authors'] == []
        assert index_data['author_exact'] is None


class TestCatalogue(TestCase):

    def test_str(self):
        # create a book and owning institution to link

        pub = Publisher(name='Pub Lee')
        pub_place = Place(name='Printington', geonames_id=4567)
        inst = OwningInstitution(name='NYSL')
        bk = Book(title='Some rambling long old title',
                  short_title='Some rambling',
                  original_pub_info='foo',
                  publisher=pub,
                  pub_place=pub_place,
                  pub_year=1823)

        cat = Catalogue(institution=inst, book=bk)
        assert '%s / %s' % (bk, inst) == str(cat)

        # with no date set
        cat.start_year = 1891
        assert '%s / %s (1891-)' % (bk, inst) == str(cat)

## tests for through models

class TestBookSubject(TestCase):
    fixtures = ['sample_book_data.json']

    def test_str(self):
        book = Book.objects.first()
        subj = Subject.objects.first()
        # non-primary subject
        bksubj = BookSubject(book=book, subject=subj)
        assert str(bksubj) == '%s %s' % (book, subj)
        # primary subject
        bksubj.is_primary = True
        assert str(bksubj) == '%s %s (primary)' % (book, subj)


class TestBookLanguage(TestCase):
    fixtures = ['sample_book_data.json']

    def test_str(self):
        book = Book.objects.first()
        lang = Language.objects.first()
        # non-primary language
        bklang = BookLanguage(book=book, language=lang)
        assert str(bklang) == '%s %s' % (book, lang)
        # primary subject
        bklang.is_primary = True
        assert str(bklang) == '%s %s (primary)' % (book, lang)


class TestCreator(TestCase):
    fixtures = ['sample_book_data.json']

    def test_str(self):
        creator = Creator.objects.first()
        assert str(creator) == \
            '%s %s %s' % (creator.person, creator.creator_type, creator.book)


class TestPersonBook(TestCase):
    fixtures = ['sample_book_data.json']

    def test_str(self):
        interaction = PersonBook(person=Person.objects.first(),
            book=Book.objects.first(),
            relationship_type=PersonBookRelationshipType.objects.first())
        # no dates set
        expected_str = '%s: %s of %s' % (interaction.person, interaction.relationship_type, interaction.book)
        assert str(interaction) == expected_str
        # with date
        interaction.start_year = 1901
        assert str(interaction) == '%s (1901-)' % expected_str


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


class TestBookViews(TestCase):
    fixtures = ['sample_book_data.json']

    def setUp(self):
        # create an admin user to test autocomplete views
        self.password = 'pass!@#$'
        self.admin = get_user_model().objects.create_superuser('testadmin',
            'test@example.com', self.password)

    def test_publisher_autocomplete(self):
        pub_autocomplete_url = reverse('books:publisher-autocomplete')
        result = self.client.get(pub_autocomplete_url,
            params={'q': 'van der'})
        # not allowed to anonymous user
        assert result.status_code == 302

        # login as an admin user
        self.client.login(username=self.admin.username, password=self.password)

        result = self.client.get(pub_autocomplete_url, {'q': 'van der'})
        assert result.status_code == 200
        # decode response to inspect
        data = json.loads(result.content.decode('utf-8'))
        assert data['results'][0]['text'] == 'E. van der Erve'

    def test_language_autocomplete(self):
        language_autocomplete_url = reverse('books:language-autocomplete')
        result = self.client.get(language_autocomplete_url,
            params={'q': 'latin'})
        # not allowed to anonymous user
        assert result.status_code == 302

        # login as an admin user
        self.client.login(username=self.admin.username, password=self.password)

        result = self.client.get(language_autocomplete_url, {'q': 'lat'})
        assert result.status_code == 200
        # decode response to inspect
        data = json.loads(result.content.decode('utf-8'))
        assert data['results'][0]['text'] == 'Latin'

    def test_subject_autocomplete(self):
        subject_autocomplete_url = reverse('books:subject-autocomplete')
        result = self.client.get(subject_autocomplete_url,
            params={'q': 'chron'})
        # not allowed to anonymous user
        assert result.status_code == 302

        # login as an admin user
        self.client.login(username=self.admin.username, password=self.password)

        result = self.client.get(subject_autocomplete_url, {'q': 'chron'})
        assert result.status_code == 200
        # decode response to inspect
        data = json.loads(result.content.decode('utf-8'))
        assert data['results'][0]['text'] == 'Chronology'

    def test_canvas_autocomplete(self):
        canvas_autocomplete_url = reverse('books:canvas-autocomplete')

        result = self.client.get(canvas_autocomplete_url,
            params={'q': '00000150'})
        # not allowed to anonymous user
        assert result.status_code == 302

        # login as an admin user
        self.client.login(username=self.admin.username, password=self.password)

        # search by partial label
        result = self.client.get(canvas_autocomplete_url, {'q': '000150'})
        assert result.status_code == 200
        data = json.loads(result.content.decode('utf-8'))
        assert data['results'][0]['id'] == '10465'
        # search by partial uri
        result = self.client.get(canvas_autocomplete_url, {'q': 'pqn59s484h'})
        data = json.loads(result.content.decode('utf-8'))
        assert data['results'][0]['id'] == '10465'

    @pytest.mark.usefixtures("solr")
    def test_book_list(self):
        url = reverse('books:list')

         # nothing indexed - should find nothing
        response = self.client.get(url)
        assert response.status_code == 200
        self.assertContains(response, 'No results')

        books = Book.objects.all()

        # index books for subsequent searches
        Indexable.index_items(books, params={'commitWithin': 500})
        sleep(2)

         # no query or filters, should find all books
        response = self.client.get(url)
        assert response.status_code == 200
        # last modified header should be set on response
        assert response.has_header('last-modified')

        # no easy way to get last modification time from Solr...
        index_modified = PagedSolrQuery({
            'q': '*:*',
            'sort': 'last_modified desc',
            'fq': 'content_type:(%s)' % str(Book._meta)
            })[0]['last_modified']
        index_modified_dt = datetime.strptime(index_modified, '%Y-%m-%dT%H:%M:%S.%fZ')

        modified = index_modified_dt.strftime('%a, %d %b %Y %H:%M:%S GMT')
        assert response['Last-Modified'] == modified

        # provisional text
        self.assertContains(response, 'Displaying %d books' % books.count())

        # NOTE: total currently not displayed
        for book in books:
            self.assertContains(response, book.short_title)
            self.assertContains(response, book.pub_year)
            for creator in book.authors():
                self.assertContains(response, creator.person.authorized_name)

        # annotated badge should be displayed for books marked as annotated
        annotated_count = books.filter(is_annotated=True).count()
        self.assertContains(response, '<div class="ui label">annotated</div>',
                            count=annotated_count)

        # associate digital edition & thumbnail from fixture
        book = books.first()
        book.digital_edition = Manifest.objects.first()
        canvas = book.digital_edition.canvases.first()
        canvas.thumbnail = True
        canvas.save()
        # add to Solr index
        book.index(params={'commitWithin': 500})
        sleep(2)

        response = self.client.get(url)
        # should include image urls (1x/2x)
        self.assertContains(response, str(canvas.image.size(height=218)))
        self.assertContains(response, str(canvas.image.size(height=436)))
        # should include image label
        self.assertContains(response, canvas.label)


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
