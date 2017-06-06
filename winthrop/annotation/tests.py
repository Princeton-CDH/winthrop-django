from django.test import TestCase
from unittest.mock import Mock

from .models import Annotation, Tag
from winthrop.books.models import Language
from winthrop.people.models import Person


class TestAnnotation(TestCase):

    def setUp(self):
        # create a person we can use for all the tests
        self.author = Person.objects.create(authorized_name='Bar, Foo')

    def test_handle_extra_data(self):

        ## -- test tag handling
        annotation = Annotation.objects.create()
        # must be saved to test related object handling

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
        annotation.handle_extra_data({'anchorLanguages': languages}, Mock())
        assert annotation.anchor_languages.count() == 3
        assoc_languages = [language.name for language in
                           annotation.anchor_languages.all()]
        # test language names against expected from list
        # order unimportant call sort() method
        assert assoc_languages.sort() == languages[:-1].sort()
        languages = languages[0:2]  # subset to English and locations
        annotation.handle_extra_data({'anchorLanguages': languages}, Mock())
        # Ancient Greek should have been removed
        assert annotation.anchor_languages.count() == 2
        assoc_languages = [language.name for language in
                           annotation.anchor_languages.all()]
        assert 'Ancient Greek' not in assoc_languages

        # test setting of local text fields and removal of quote/text
        text_dict = {
            'translation': 'text of translation',
            'anchorTranslation': 'text of anchor translation',
            'quote': 'foo',
            'text': 'bar'
        }
        # make a copy because the expected behavior is to delete the dict
        copy = text_dict.copy()
        annotation.handle_extra_data(copy, Mock())
        # all of the object fields should equal their dict equivalent
        assert annotation.text_translation == text_dict['translation']
        assert annotation.anchor_translation == text_dict['anchorTranslation']
        # if a field is deleted from the dict, it should be deleted from object
        # by hande_extra_data
        # remove translation
        text_dict.pop('translation')
        copy = text_dict.copy()
        annotation.handle_extra_data(copy, Mock())
        assert not annotation.text_translation
        assert annotation.anchor_translation == text_dict['anchorTranslation']
        # check that copy dict is empty
        assert not copy

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
        assert annotation.info()['anchorLanguages']
        # it should have all three languages
        assert len(annotation.info()['anchorLanguages']) == 3
        # it should have those specific languages, order unimportant so sort()
        assert annotation.info()['anchorLanguages'].sort() == languages.sort()

        # set local text fields
        # NOTE: Not quote, because that's part of the built in functionality
        # of django-annotator-store
        text_dict = {
            'text_translation': 'text of translation',
            'anchor_translation': 'text of anchor translation',
        }
        annotation = Annotation.objects.create(**text_dict)
        assert annotation.info()['translation'] == text_dict['text_translation']
        assert annotation.info()['anchorTranslation'] == text_dict['anchor_translation']


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
