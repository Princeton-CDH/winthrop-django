from collections import defaultdict
import csv
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
try:
    # django 1.10
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
import json
import os
from io import StringIO

from winthrop.places.models import Place
from winthrop.people.models import Person
from .models import OwningInstitution, Book, Publisher, Catalogue, \
    Creator, CreatorType
from .management.commands import import_nysl


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

        pl = Place.objects.first()
        inst = OwningInstitution.objects.create(name='NYSL',
            place=pl)
        # new institution has no books associated
        assert inst.book_count() == 0

        # create a book and associated it with the institution
        pub = Publisher.objects.create(name='Pub Lee')
        bk = Book.objects.create(title='Some rambling long old title',
            short_title='Some rambling',
            original_pub_info='foo',
            publisher=pub, pub_place=pl, pub_year=1823,
            is_extant=False, is_annotated=False, is_digitized=False)

        cat = Catalogue.objects.create(institution=inst, book=bk,
            is_current=False, is_sammelband=False)

        assert inst.book_count() == 1


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



# TODO: do we want/need tests for through models?
# book-subject, book-language, creator, person-book
# Expect to have more sophisticated/meaningful things to test
# as we add functionality.

class TestImportNysl(TestCase):

    test_csv = os.path.join(FIXTURE_DIR, 'test_nysl_data.csv')

    def setUp(self):
        self.cmd = import_nysl.Command()
        self.cmd.stdout = StringIO()
        # setup normally done in handle()
        self.cmd.stats = defaultdict(int)
        self.cmd.nysl = OwningInstitution.objects.get(short_name='NYSL')

    def test_run(self):
        out = StringIO()
        call_command('import_nysl', self.test_csv, stdout=out)
        output = out.getvalue()
        assert 'Imported content' in output
        assert '2 books' in output
        assert '2 places' in output
        assert '2 people' in output
        assert '2 publishers' in output

    def test_create_book(self):
        # load data from fixture to test book creation more directly
        with open(self.test_csv) as csvfile:
            csvreader = csv.DictReader(csvfile)
            de_christelicke = next(csvreader)
            mercurii = next(csvreader)

        # test against first row of fixture data
        data = de_christelicke
        self.cmd.create_book(data)
        # find book object by short title and compare data
        book = Book.objects.get(short_title=data['Short Title'])
        assert book.title == data['Title']
        assert book.pub_year == int(data['Year of Publication'])
        assert book.is_extant
        assert book.original_pub_info == data['PUB INFO - Original']
        assert not book.is_annotated
        assert book.notes == data['Notes']
        # test fields on related models
        assert book.pub_place.name == data['Modern Place of Publication']
        assert book.publisher.name == data['Standardized Name of Publisher']
        # - first row has author, no editor or translator
        assert book.authors().first().person.authorized_name == \
            data['AUTHOR, Standarized']
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
        self.cmd.create_book(data)
        # find book object by short title and compare data
        book = Book.objects.get(short_title=data['Short Title'])
        assert book.red_catalog_number == data['RED catalogue number at the front']
        # ink and pencil are 'NA' in fixture; should be empty
        assert book.ink_catalog_number == ''
        assert book.pencil_catalog_number == ''


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


