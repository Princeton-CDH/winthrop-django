import json
from unittest.mock import patch, Mock
import os

from django.db.models.query import QuerySet
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.test import TestCase
from django.urls import reverse
from djiffy.models import Manifest
import pytest
from unidecode import unidecode

from winthrop.annotation.models import Annotation
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

    def test_annotators(self):
        de_christelicke = Book.objects.get(short_title__contains="De Christelicke")
        # no annotators by default in fixture
        de_christelicke.annotators().count() == 0
        # create an annotation to check
        # get the first manifest from the fixture
        de_christelicke.digital_edition = Manifest.objects.first()
        de_christelicke.save()
        canvas = de_christelicke.digital_edition.canvases.first()
        person = Person.objects.first()
        # create annotation with first person in manifest
        Annotation.objects.create(
            canvas=canvas,
            author=person
        )
        # should be one annotator, and that annotator should be person
        de_christelicke.annotators().count() == 1
        de_christelicke.annotators() == Person.objects\
            .filter(annotation__canvas__manifest__book=de_christelicke)

    def test_authors(self):
        de_christelicke = Book.objects.get(short_title__contains="De Christelicke")

        laski = 'Łaski, Jan'
        assert de_christelicke.authors().count() == 1
        assert de_christelicke.authors().first().authorized_name == \
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

        # unsaved object - no error, empty result
        book = Book()
        assert not book.authors()

    def test_editors(self):
        de_christelicke = Book.objects.get(short_title__contains="De Christelicke")

        # no editors
        assert de_christelicke.editors().count() == 0

        # convert author to editor
        laski = 'Łaski, Jan'
        ed_type = CreatorType.objects.get(name='Editor')
        de_christelicke.creator_set.update(creator_type=ed_type)
        assert de_christelicke.editors().count() == 1
        assert de_christelicke.editors().first().authorized_name == \
            laski

        # unsaved object - no error, empty result
        book = Book()
        assert not book.editors()

    def test_translators(self):
        de_christelicke = Book.objects.get(short_title__contains="De Christelicke")

        # no translators
        assert de_christelicke.translators().count() == 0

        # convert author to translator
        laski = 'Łaski, Jan'
        translator = CreatorType.objects.get(name='Translator')
        de_christelicke.creator_set.update(creator_type=translator)
        assert de_christelicke.translators().count() == 1
        assert de_christelicke.translators().first().authorized_name == \
            laski

        # unsaved object - no error, empty result
        book = Book()
        assert not book.translators()


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
    def test_handle_related_delete(self, mock_index_items):
        author = Person.objects.all().first()
        book = Book.objects.filter(contributors=author).first()

        Book.handle_related_delete(Mock(), author)

        assert author.book_set.count() == 0
        args, kwargs = mock_index_items.call_args
        assert isinstance(args[0], QuerySet)
        assert book in args[0]
        assert kwargs['params'] == {'commitWithin': 3000}

    @patch.object(Indexable, 'index_items')
    def test_handle_named_save(self, mock_index_items):
        # - create a book with a subject attached
        subject = Subject.objects.all().first()
        book = Book.objects.first()
        BookSubject.objects.create(
            subject=subject,
            book=book,
            is_primary=True,
        )
        # no change in name, not called
        Book.handle_named_save(Mock(), subject)
        assert not mock_index_items.called
        subject.name = 'Test'

        Book.handle_named_save(Mock(), subject)
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
            assert auth.authorized_name in index_data['author']
        assert index_data['pub_year'] == book.pub_year
        assert not index_data['thumbnail']
        assert not index_data['thumbnail_label']
        assert index_data['author_sort'] == book.authors()[0].authorized_name
        assert index_data['author'] == [str(author) for author in book.authors()]
        assert index_data['publisher'] == book.publisher.name
        assert index_data['pub_place'] == book.pub_place.name
        assert index_data['original_pub_info'] == book.original_pub_info
        assert index_data['notes'] == book.notes

        # delete publisher, pub place to check error handling
        book.publisher = None
        book.pub_place = None
        index_data = book.index_data()
        assert index_data['publisher'] == ''
        assert index_data['pub_place'] == ''


        # associate digital edition from fixture (has no thumbnail)
        book.digital_edition = Manifest.objects.first()
        # save so its real for other database lookups
        book.save()
        # has digital edition but no thumbnail
        # book = Book.objects.filter(digital_edition__isnull=False).first()
        index_data = book.index_data()
        assert not index_data['thumbnail']
        assert not index_data['thumbnail_label']
        assert index_data['author_sort'] == book.authors()[0].authorized_name
        assert index_data['author'] == [str(author) for author in book.authors()]

        # mark canvas as thumbnail
        canvas = book.digital_edition.canvases.first()
        canvas.thumbnail = True
        canvas.save()
        index_data = book.index_data()
        assert index_data['thumbnail'] == canvas.iiif_image_id
        assert index_data['thumbnail_label'] == canvas.label

        # no annotators
        index_data = book.index_data()
        assert index_data['annotator'] == []
        # add annotator
        Annotation.objects.create(
            author=Person.objects.first(),
            canvas=canvas,
            uri=canvas.uri,
        )
        index_data = book.index_data()
        assert index_data['annotator'] == [str(Person.objects.first())]

        # no authors
        book.creator_set.all().delete()
        index_data = book.index_data()
        assert index_data['author'] == []

        # editors
        # no editors in fixture
        book = Book.objects.first()
        index_data = book.index_data()
        assert index_data['editor'] == []
        # add editors
        person = Person.objects.first()
        person2 = Person.objects.last()
        book.add_editor(person)
        book.add_editor(person2)
        index_data = book.index_data()
        # using 'in' because it's order agnostic
        assert str(person) in index_data['editor']
        assert str(person2) in index_data['editor']

        # translators
        book = Book.objects.last()
        index_data = book.index_data()
        assert index_data['translator'] == []
        # add editors
        person = Person.objects.first()
        person2 = Person.objects.last()
        book.add_translator(person)
        book.add_translator(person2)
        index_data = book.index_data()
        # using 'in' because it's order agnostic
        assert str(person) in index_data['translator']
        assert str(person2) in index_data['translator']

        # no languages on books in fixture, so test that state first
        index_data = book.index_data()
        assert index_data['language'] == []
        # now add languages and assert that they are in index_data
        english = Language.objects.get(name='English')
        french = Language.objects.get(name='French')
        BookLanguage.objects.bulk_create([
            BookLanguage(book=book, language=english, is_primary=True),
            BookLanguage(book=book, language=french, is_primary=False),
        ])
        index_data = book.index_data()
        assert str(english) in index_data['language']
        assert str(french) in index_data['language']

        # no subjects in book fixture
        index_data = book.index_data()
        assert index_data['subject'] == []
        # add subjects and assert that they are in index_data
        alchemy = Subject.objects.get(name='Alchemy')
        historia = Subject.objects.get(name='Historia')
        BookSubject.objects.bulk_create([
            BookSubject(book=book, subject=alchemy, is_primary=True),
            BookSubject(book=book, subject=historia, is_primary=True),
        ])
        index_data = book.index_data()
        assert str(alchemy) in index_data['subject']
        assert str(historia) in index_data['subject']

    def test_generate_slug(self):
        # model method
        book = Book.objects.all().first()
        slug = book.generate_slug()
        book_author_lastname = book.authors().first().authorized_name.split(',')[0]
        book_author_lastname = unidecode(book_author_lastname).strip().lower()
        assert slug.startswith(book_author_lastname)
        assert slug.endswith('-%s' % book.pub_year)
        # title shortened to first 5 words
        shorter_title = ' '.join(book.short_title.split()[:5])
        assert slugify(shorter_title) in slug

        # no pub year, no problem
        book.pub_year = None
        author_title_slug = slugify('%s %s' % (book_author_lastname, shorter_title))
        assert book.generate_slug() == author_title_slug

        # no author, no problem
        book.creator_set.all().delete()
        assert book.generate_slug() == slugify(shorter_title)

        # long title is shortened
        book.short_title = book.title
        assert book.generate_slug() == slugify(' '.join(book.short_title.split()[:5]))

    def test_save(self):
        # save should generate slug if not set
        book = Book.objects.all().first()
        book.slug = None
        book.save()
        assert book.slug == book.generate_slug()

        # not regenerated on save if already set
        test_slug = 'my-bogus-slug'
        book.slug = test_slug
        book.save()
        assert book.slug == test_slug


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
