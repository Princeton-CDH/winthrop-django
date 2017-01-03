from django.test import TestCase
import pytest

from winthrop.places.models import Place
from .models import OwningInstitution, Book, Publisher, Catalogue


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

        assert 1 == inst.book_count()


class TestBook(TestCase):

    def test_str(self):
        pub = Publisher(name='Pub Lee')
        pub_place = Place(name='Printington', geonames_id=4567)

        bk = Book(title='Some rambling long old title',
            short_title='Some rambling',
            original_pub_info='foo',
            publisher=pub,
            pub_place=pub_place,
            pub_year=1823)

        assert 'Some rambling (1823)' == str(bk)


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