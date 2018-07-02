import json
from unittest.mock import patch, Mock
import os

from django.db.models.query import QuerySet
from django.utils.safestring import mark_safe
from django.test import TestCase
from django.urls import reverse
from djiffy.models import Manifest
import pytest

from winthrop.books.models import OwningInstitution, Book, Publisher, Catalogue, \
    Creator, CreatorType, Subject, BookSubject, Language, BookLanguage, \
    PersonBook, PersonBookRelationshipType
from winthrop.common.solr import Indexable
from winthrop.places.models import Place
from winthrop.people.models import Person


FIXTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           '..', 'fixtures')


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