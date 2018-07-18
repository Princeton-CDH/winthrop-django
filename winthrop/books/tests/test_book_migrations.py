import os
import pickle
import re
from unittest.mock import patch

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase
from django.utils.text import slugify
import pytest

from winthrop.annotation.models import Annotation

FIXTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           '..', 'fixtures')

## migration test case adapted from
# https://www.caktusgroup.com/blog/2016/02/02/writing-unit-tests-django-migrations/

class TestMigrations(TransactionTestCase):

    # @property
    # def app(self):
    #     return apps.get_containing_app_config(type(self).__module__).name
    app = None
    migrate_from = None
    migrate_to = None

    def setUp(self):
        assert self.migrate_from and self.migrate_to, \
            "TestCase '{}' must define migrate_from and migrate_to properties".format(type(self).__name__)
        self.migrate_from = [(self.app, self.migrate_from)]
        self.migrate_to = [(self.app, self.migrate_to)]
        executor = MigrationExecutor(connection)
        old_apps = executor.loader.project_state(self.migrate_from).apps

        # Reverse to the original migration
        executor.migrate(self.migrate_from)

        self.setUpBeforeMigration(old_apps)

        # Run the migration to test
        executor.loader.build_graph()  # reload.
        executor.migrate(self.migrate_to)

        self.apps = executor.loader.project_state(self.migrate_to).apps

    def setUpBeforeMigration(self, apps):
        pass


# NOTE: TransactionTestCase must be run after all other test cases,
# because it truncates the database, removing fixture objects expected
# to be present by other tests.
# Django test runner runs transaction test cases after simple test cases,
# but pytest / pytest-django do not.


@pytest.mark.last
class TestBookAddSlugs(TestMigrations):

    app = 'books'
    migrate_from = '0011_add_book_digital_edition_remove_is_digitized'
    migrate_to = '0014_make_book_slugs_unique'
    serialized_rollback = True

    def setUpBeforeMigration(self, apps):
        # create variant books to test
        Book = apps.get_model('books', 'Book')
        self.noauthor_noyear_id = Book.objects.create(short_title='Authorless').id
        self.noauthor_year_id = Book.objects.create(short_title='Authorless',
                                                    pub_year=1701).id

        Person = apps.get_model('people', 'Person')
        Creator = apps.get_model('books', 'Creator')
        CreatorType = apps.get_model('books', 'CreatorType')

        princeps = Book.objects.create(short_title='Princeps', pub_year=1622)
        machiavelli = Person.objects.create(authorized_name='Machiavelli, Niccolo')
        author = CreatorType.objects.get(name='Author')
        Creator.objects.create(person=machiavelli, book=princeps, creator_type=author)
        self.princeps_id = princeps.id

    def test_slugs_generated(self):
        Book = self.apps.get_model('books', 'Book')
        authorless_book = Book.objects.get(id=self.noauthor_noyear_id)
        assert authorless_book.slug == slugify(authorless_book.short_title)

        authorless_book = Book.objects.get(id=self.noauthor_year_id)
        assert authorless_book.slug == \
            slugify('%s %s' % (authorless_book.short_title, authorless_book.pub_year))

        princeps = Book.objects.get(id=self.princeps_id)
        assert princeps.slug == \
            slugify('Machiavelli %s %s' % (princeps.short_title, princeps.pub_year))


@pytest.mark.last
class TestMigratePlumToFiggy(TestMigrations):

    app = 'books'
    migrate_from = '0014_make_book_slugs_unique'
    migrate_to = '0015_plum_to_figgy'
    serialized_rollback = True

    # loads a book with the old plum manifest and related canvas with
    # i.e., most complex example that should be handled correctly
    fixtures = ['test_plum_figgy']

    @patch('winthrop.books.migrations.0015_plum_to_figgy.iiif')
    @patch('winthrop.books.migrations.0015_plum_to_figgy.IIIFPresentation')
    @patch('winthrop.books.migrations.0015_plum_to_figgy.requests')
    def setUp(self, mockrequests, mockpres, mockiiif):
        # mock out data fixtures for calls to figgy
        requestpickle = os.path.join(FIXTURE_DIR, "test_plum_figgy_request.pickle")
        newmanif = os.path.join(FIXTURE_DIR, "test_plum_figgy_newmanif.pickle")
        iiif = os.path.join(FIXTURE_DIR, "test_plum_figgy_iiif.pickle")

        with open(requestpickle, "rb") as data:
            response = pickle.load(data)
        with open(newmanif, "rb") as data:
            newmanif = pickle.load(data)
        with open(iiif, "rb") as data:
            iiif_list = pickle.load(data)
        self.iiif_list = iiif_list
        # response from figgy
        mockrequests.head.return_value = response
        # manifests for this book from Figgy
        mockpres.from_url.return_value = newmanif
        mockpres.short_id.return_value = 'e75a2026-cf91-40d0-b592-176faae9b12c'
        # mocks for iiif calls
        # first element is a list of IIIF images init'd from url
        # second element is a lost of IIIF images from figgy
        mockiiif.IIIFImageClient.init_from_url.side_effect = iiif_list[0]
        mockiiif.IIIFImageClient.side_effect = iiif_list[1]

        super().setUp()

    def test_plum_to_figgy(self):
        Manifest = self.apps.get_model('djiffy', 'Manifest')
        # there should be one manifest
        assert Manifest.objects.count() == 1
        # retrieve that manifest
        manif = Manifest.objects.all()[0]
        # check that the manifest's uri has figgy and not plum
        assert 'plum.princeton' not in manif.uri
        assert 'figgy.princeton' in manif.uri
        # check that we have a uuid for the identifier
        # https://stackoverflow.com/questions/136505/searching-for-uuids-in-text-with-regex/14166194
        uuid_regex = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')
        assert re.search(uuid_regex, manif.uri)
        assert re.search(uuid_regex, manif.short_id)
        # check that canvases have no plum in their ids and a UUID
        for canvas in manif.canvases.all():
            assert re.search(uuid_regex, canvas.uri)
            assert 'plum.princeton' not in manif.uri
            assert 'figgy.princeton' in manif.uri
        # check that annotations and images are set correctly
        # the only change in the uris is the inclusion of
        # full/!1000,1000/ in the uri
        for ann in Annotation.objects.all():
            src = ann.extra_data['image_selection']['src']
            uri = ann.extra_data['image_selection']['uri']
            assert 'full/full' not in src
            assert 'full/full' not in uri
            assert 'full/!1000,1000/' in src
            assert 'full/!1000,1000/' in src
