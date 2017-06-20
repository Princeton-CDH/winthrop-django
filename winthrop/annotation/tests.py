import json
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from django.urls import reverse

from djiffy.models import Manifest, Canvas

from .models import Annotation, Tag
from .admin import CanvasLinkWidget
from winthrop.books.models import Book, Language, PersonBook, \
    PersonBookRelationshipType
from winthrop.people.models import Person
from .admin import WinthropAnnotationAdmin


class TestAnnotation(TestCase):

    def setUp(self):
        # create a person we can use for all the tests
        book = Book.objects.create(title='Long title', short_title='Long',
            original_pub_info='fake pub info')
        self.author = Person.objects.create(authorized_name='Bar, Foo')
        self.pb = PersonBook.objects.create(book=book, person=self.author,
            relationship_type=PersonBookRelationshipType.objects.get(pk=1))

    def test_save(self):
        # canvas automatically associated by uri on save
        manif = Manifest.objects.create()
        canvas = Canvas.objects.create(uri='http://so.me/iiif/id/',
            order=0, manifest=manif)
        note = Annotation.objects.create(uri=canvas.uri)
        assert note.canvas == canvas

        # how to check that canvas db lookup is skipped when not needed?
        with patch('winthrop.annotation.models.Canvas') as mockcanvas:
            mockcanvas.DoesNotExist = Canvas.DoesNotExist
            note.save()
            mockcanvas.objects.get.assert_not_called()

            # if uri changes, canvas should be cleared
            mockcanvas.objects.get.side_effect = Canvas.DoesNotExist
            note.uri = 'http://some.thing/else'
            note.save()
            assert not note.canvas
            mockcanvas.objects.get.assert_called_with(uri=note.uri)


    def test_handle_extra_data(self):

        # Create a blank annotation object
        # Don't save it because we want to check that handle_extra_data()
        # calls the save before adding tags

        annotation = Annotation()
        # test adding new tags
        # - using three existing tags and one nonexistent
        tags = ['manicule', 'underlining', 'dash', 'bogus']
        data = annotation.handle_extra_data({'tags': tags},
            Mock())   # NOTE: using Mock() for request - currently unused
        # existing tags should be associated with annotation
        assert annotation.tags.count() == 3
        saved_tags = [tag.name for tag in annotation.tags.all()]
        for tag in tags[:-1]:
            assert tag in saved_tags
        # bogus tag should be ignored
        assert 'bogus' not in saved_tags
        # tags should be removed from annotation extra data
        assert 'tags' not in data

        # test changing the list of existing tags
        tags = ['manicule', 'dash']
        annotation.handle_extra_data({'tags': tags}, Mock())
        assert annotation.tags.count() == 2
        # underlining should be removed
        saved_tags = [tag.name for tag in annotation.tags.all()]
        assert 'underlining' not in saved_tags

        # test removing existing tags
        annotation.handle_extra_data({'tags': []}, Mock())
        assert annotation.tags.count() == 0

        # test adding author in database
        annotation.handle_extra_data({'author': 'Bar, Foo'}, Mock())
        # check that an author is set
        assert annotation.author
        # check that it is Mr. Foo Bar
        assert annotation.author == self.author

        # empty author field should unset author on annotation
        annotation.handle_extra_data({'author': ''}, Mock())
        assert not annotation.author

        # an incorrect authorized_name should also do the same
        annotation.handle_extra_data({'author': 'Bar, Foo'}, Mock())
        # check that an author is set
        assert annotation.author
        # dud author should unset the field
        annotation.handle_extra_data({'author': 'Bar, Foobaz'}, Mock())
        assert not annotation.author

        # an author not in the list of annotators should unset
        annotation.handle_extra_data({'author': 'Bar, Foo'}, Mock())
        # check that an author is set
        assert annotation.author
        # delete relationship
        pb = self.pb
        pb.delete()
        # handle_extra_data again
        annotation.handle_extra_data({'author': 'Bar, Foo'}, Mock())
        assert not annotation.author


        # test setting languages (including not setting a language not in database)
        languages = ['English', 'Latin', 'Ancient Greek', 'Lojban']
        annotation.handle_extra_data({'languages': languages}, Mock())
        assert annotation.languages.count() == 3
        assoc_languages = [language.name for language in
                           annotation.languages.all()]
        # test language names against expected from list
        # order unimportant call sort() method
        assert assoc_languages.sort() == languages[:-1].sort()
        languages = languages[0:2]  # subset to English and locations
        annotation.handle_extra_data({'languages': languages}, Mock())
        # Ancient Greek should have been removed
        assert annotation.languages.count() == 2
        assoc_languages = [language.name for language in
                           annotation.languages.all()]
        assert 'Ancient Greek' not in assoc_languages
        # clear to avoid false results in anchor_languages test block
        annotation.languages.clear()


        # test setting anchor_language (including not setting a language not in database)
        languages = ['English', 'Latin', 'Ancient Greek', 'Lojban']
        annotation.handle_extra_data({'anchor_languages': languages}, Mock())
        assert annotation.anchor_languages.count() == 3
        assoc_languages = [language.name for language in
                           annotation.anchor_languages.all()]
        # test language names against expected from list
        # order unimportant call sort() method
        assert assoc_languages.sort() == languages[:-1].sort()
        languages = languages[0:2]  # subset to English and locations
        annotation.handle_extra_data({'anchor_languages': languages}, Mock())
        # Ancient Greek should have been removed
        assert annotation.anchor_languages.count() == 2
        assoc_languages = [language.name for language in
                           annotation.anchor_languages.all()]
        assert 'Ancient Greek' not in assoc_languages

        # test setting of local text fields and removal of quote/text
        text_dict = {
            'translation': 'text of translation',
            'anchor_translation': 'text of anchor translation',
        }
        # make a copy because the expected behavior is to delete the dict
        copy = text_dict.copy()
        annotation.handle_extra_data(copy, Mock())
        # all of the object fields should equal their dict equivalent
        assert annotation.text_translation == text_dict['translation']
        assert annotation.anchor_translation == text_dict['anchor_translation']
        # if a field is deleted from the dict, it should be deleted from object
        # by hande_extra_data
        # remove translation
        text_dict.pop('translation')
        copy = text_dict.copy()
        annotation.handle_extra_data(copy, Mock())
        assert not annotation.text_translation
        assert annotation.anchor_translation == text_dict['anchor_translation']
        # check that copy dict is empty
        assert not copy

        # test setting subjects (including not setting a subject not in database)
        subjects = ['Phrenology', 'Chronology', 'Commentary']
        annotation.handle_extra_data({'subjects': subjects}, Mock())
        assert annotation.subjects.count() == 2
        assoc_subjects = [subject.name for subject in
                      annotation.subjects.all()]
        # test subject names against expected from list (all but first)
        # (using set to compare without order)
        assert set(assoc_subjects) == set(subjects[1:])
        subjects = ['Commentary']
        annotation.handle_extra_data({'subjects': subjects}, Mock())
        # Chronology should have been removed
        assert annotation.subjects.count() == 1
        assoc_subjects = [subject.name for subject in
                           annotation.subjects.all()]
        assert 'Chronology' not in assoc_subjects

    def test_info(self):
        annotation = Annotation.objects.create()
        # tags should be an empty list when none are set
        assert not annotation.info()['tags']
        tags = ['manicule', 'dash']
        annotation.handle_extra_data({'tags': tags}, Mock())
        # order not guaranteed / not important; sort for comparison
        assert annotation.info()['tags'].sort() == tags.sort()

        # test author - author should be empty in info
        assert 'author' not in annotation.info()
        # set an author
        annotation.handle_extra_data({'author': 'Bar, Foo'}, Mock())
        # author should be added to the fields
        assert annotation.info()['author']
        # name and id should be set from database
        assert annotation.info()['author'] == \
            self.author.authorized_name

        # set languages on annotation object
        languages = ['English', 'Latin', 'German']
        annotation.languages.set(Language.objects.filter(name__in=languages))
        # language key should exist
        assert annotation.info()['languages']
        # it should have all three languages
        assert len(annotation.info()['languages']) == 3
        # it should have those specific languages, order unimportant so sort()
        assert annotation.info()['languages'].sort() == languages.sort()

        # set anchor languages on annotation object
        languages = ['English', 'Latin', 'German']
        annotation.anchor_languages.set(Language.objects.filter(name__in=languages))
        # anchorLanguage key should exist
        assert annotation.info()['anchor_languages']
        # it should have all three languages
        assert len(annotation.info()['anchor_languages']) == 3
        # it should have those specific languages, order unimportant so sort()
        assert annotation.info()['anchor_languages'].sort() == languages.sort()

        # set local text fields
        # NOTE: Not quote, because that's part of the built in functionality
        # of django-annotator-store
        text_dict = {
            'text_translation': 'text of translation',
            'anchor_translation': 'text of anchor translation',
        }
        annotation = Annotation.objects.create(**text_dict)
        assert annotation.info()['translation'] == text_dict['text_translation']
        assert annotation.info()['anchor_translation'] == text_dict['anchor_translation']

    def test_iiif_image_selection(self):
        annotation = Annotation()
        # no canvas or image selection
        assert not annotation.iiif_image_selection()

        annotation.canvas = Canvas()
        # canvas set but no image region
        assert not annotation.iiif_image_selection()

        # both canvas and image region set
        annotation.extra_data['image_selection'] = {
            'x': "21.58%",
            'y': "49.40%",
            'h': "13.50%",
            'w': "24.68%"
        }
        img = annotation.iiif_image_selection()
        # should return a piffle iiif image object
        assert img
        iiif_region_info = img.region.as_dict()
        assert iiif_region_info['percent']
        assert iiif_region_info['x'] == 21.58
        assert iiif_region_info['y'] == 49.4
        assert iiif_region_info['width'] == 24.68
        assert iiif_region_info['height'] == 13.5

    def test_admin_thumbnail(self):
        annotation = Annotation()
        # no canvas or image selection
        assert not annotation.admin_thumbnail()

        annotation.canvas = Canvas()
        # canvas set but no image region
        assert annotation.admin_thumbnail() == \
            '<img src="%s" />' % annotation.canvas.image.mini_thumbnail()

        # both canvas and image region set
        annotation.extra_data['image_selection'] = {
            'x': "21.58%",
            'y': "49.40%",
            'h': "13.50%",
            'w': "24.68%"
        }
        assert annotation.admin_thumbnail() == \
            '<img src="%s" />' % annotation.iiif_image_selection().mini_thumbnail()


class TestTag(TestCase):

    def setUp(self):
        self.basic_annotation_dict = {
            'text_translation': 'Translation of text',
            'anchor_translation': 'Anchor text translation',
            'quote': 'Annotation text',
        }

    def test_str(self):
        tag = Tag(name='foo')
        assert str(tag) == 'foo'

    def test_associate_with_annotation(self):
        tag = Tag.objects.create(name='foo')
        test_annotation = Annotation.objects.create(**self.basic_annotation_dict)
        test_annotation.tags.add(tag)
        assert test_annotation.tags.first() == tag


class TestCanvasLinkWidget(TestCase):
    fixtures = ['sample_book_data.json']

    def test_render(self):
        widget = CanvasLinkWidget()
        # no value set - should not error or include canvas
        rendered = widget.render('canvas', None, {'id': 1})
        assert 'canvas-link' not in rendered

        # canvas id set - should includ link
        canvas = Canvas.objects.all().first()
        rendered = widget.render('person', canvas.id, {'id': 1234})
        assert 'View canvas on site' in rendered
        assert canvas.get_absolute_url() in rendered


class TestAnnotationViews(TestCase):
    fixtures = ['sample_book_data.json']

    def setUp(self):
        # create an admin user to test autocomplete views
        self.password = 'pass!@#$'
        self.admin = get_user_model().objects.create_superuser('testadmin',
            'test@example.com', self.password)

    def test_tag_autocomplete(self):
        tag_autocomplete_url = reverse('annotation:tag-autocomplete')
        result = self.client.get(tag_autocomplete_url,
            params={'q': 'ciph'})
        # not allowed to anonymous user
        assert result.status_code == 302

        # login as an admin user
        self.client.login(username=self.admin.username, password=self.password)

        result = self.client.get(tag_autocomplete_url, {'q': 'ciph'})
        assert result.status_code == 200
        # decode response to inspect
        data = json.loads(result.content.decode('utf-8'))
        assert data['results'][0]['text'] == 'cipher'

    def test_canvas_detail(self):
        # canvas detail logic is tested in djiffy,
        # but test local customization to catch any
        # breaks in the template rendering
        canvas = Canvas.objects.all().first()
        canvas_url = reverse('djiffy:canvas',
            kwargs={'manifest_id': canvas.manifest.short_id, 'id': canvas.short_id})
        response = self.client.get(canvas_url)
        self.assertTemplateUsed(response, 'djiffy/canvas_detail.html')
        self.assertNotContains(response, 'annotator.min.js',
            msg_prefix='Annotator not enabled for user without annotation add permission')

        # login as an admin user
        self.client.login(username=self.admin.username, password=self.password)
        response = self.client.get(canvas_url)
        self.assertContains(response, 'css/winthrop-annotator.css',
            msg_prefix='canvas detail page includes local annotator styles')
        # check that expected autocomplete urls are present
        self.assertContains(response, reverse('books:language-autocomplete'),
            msg_prefix='annotator init includes language autocomplete url')
        self.assertContains(response, reverse('books:subject-autocomplete'),
            msg_prefix='annotator init includes subject autocomplete url')
        self.assertContains(response, reverse('people:autocomplete', args=['annotator']),
            msg_prefix='annotator init includes annotator autocomplete url')
        self.assertContains(response, reverse('annotation:tag-autocomplete'),
            msg_prefix='annotator init includes tag autocomplete url')
        self.assertContains(response,
            'app.ident.identity = "%s";' % self.admin.username,
            msg_prefix='Logged in user username passed to annotator')


class TestWinthropAnnotationAdmin(TestCase):
    def setUp(self):
        self.author = Person.objects.create(authorized_name='Bar, Foo')
        self.site = AdminSite()

    def test_annotator(self):
        # Make sure that the list view override is working as intended
        # It should return 'Annotation Type' and set sorting based on
        # author__authorized_name
        annotation = Annotation(author=self.author)
        admin = WinthropAnnotationAdmin(Annotation, self.site)
        # Label is set to Annotator
        assert admin.annotator.short_description == 'Annotator'
        # Returns the author as the object to display
        assert admin.annotator(annotation) == self.author
