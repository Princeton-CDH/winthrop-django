from django.test import TestCase
from unittest.mock import Mock

from .models import Annotation, Tag
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

        # test adding author in data base
        annotation = Annotation.objects.create()
        annotation.handle_extra_data({
            'author': {'authorized_name': 'Bar, Foo', 'id': self.author.pk}
            },
            Mock()
        )

        # check that an author is set
        assert annotation.author
        # check that it is Mr. Foo Bar
        assert annotation.author == self.author

        # empty author field should unset author on annotation
        annotation.handle_extra_data({'author': ''}, Mock())
        assert not annotation.author

        # an author field that passes an author without id should
        # also unset the author
        # set an author
        annotation.handle_extra_data({
            'author': {'authorized_name': 'Bar, Foo', 'id': self.author.pk}
            },
            Mock()
        )
        # check that an author is set
        assert annotation.author
        annotation.handle_extra_data({
            'author': {'authorized_name': 'Barz, Foo'}
            },
            Mock()
        )
        # Dud author should unset the field
        assert not annotation.author

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
        annotation.handle_extra_data({
            'author': {'authorized_name': 'Bar, Foo', 'id': self.author.pk}
            },
            Mock()
        )
        # author should be added to the fields
        assert annotation.info()['author']
        # name and id should be set from database
        assert annotation.info()['author']['name'] == \
            self.author.authorized_name
        assert annotation.info()['author']['id'] == self.author.pk


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
