import json
import os
import re
from unittest.mock import Mock, patch

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase
from django.utils.text import slugify
import pytest
import requests

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
class TestMigratePlumToFiggy(TestMigrations):

    app = 'books'
    migrate_from = '0011_add_book_digital_edition_remove_is_digitized'
    migrate_to = '0012_plum_to_figgy'
    serialized_rollback = True

    # loads a book with the old plum manifest and related canvas with
    # i.e., most complex example that should be handled correctly
    fixtures = ['test_plum_figgy']

    @patch('djiffy.models.requests')
    @patch('winthrop.books.migrations.0012_plum_to_figgy.requests')
    def setUp(self, mockrequests, mockdjiffyrequests):
        # By mocking out requests in the two places where it appears, the
        # fixture provides mocked manifest data and constructs. The uri
        # below supplies the remaining information.

        # The test_plum_figgy_manifest fixture was produced by using the
        # .json() method of a request response to the actual manifest uri

        manifest_uri = 'https://figgy.princeton.edu/concern/scanned_resources/e75a2026-cf91-40d0-b592-176faae9b12c/manifest'

        # redirect response from figgy
        mockresponse = Mock()
        mockresponse.status_code = requests.codes.found
        mockresponse.headers = {'location': manifest_uri}
        mockrequests.head.return_value = mockresponse

        # mocks for IIIFManifest, patched in to djiffy logic so that
        # it can provide a manifest and let IIIFManifest.from_url actually
        # run
        mockdjiffyresponse = Mock()
        mockdjiffyresponse.status_code = requests.codes.ok
        raw_json = os.path.join(FIXTURE_DIR, "test_plum_figgy_manifest.json")
        with open(raw_json, "r") as data:
            mockdjiffyresponse.json.return_value = json.load(data)
        mockdjiffyrequests.get.return_value = mockdjiffyresponse
        # since mocking requests, also need to provide this info for Djiffy
        mockdjiffyrequests.codes.ok = 200

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
