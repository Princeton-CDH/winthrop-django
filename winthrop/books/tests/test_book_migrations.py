from django.apps import apps
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase
from django.utils.text import slugify
import pytest



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

