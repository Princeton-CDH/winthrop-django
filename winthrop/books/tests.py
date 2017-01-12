from django.test import TestCase
import pytest

from winthrop.places.models import Place
from winthrop.people.models import Person
from .models import OwningInstitution, Book, Publisher, Catalogue, \
    Creator, CreatorType


class TestOwningInstitution(TestCase):

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

        pl = Place.objects.create(name='Printington', geonames_id=4567)
        inst = OwningInstitution.objects.create(name='NYSL',
            place=pl)
        # new institution has no books associated
        assert 0 == inst.book_count()

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