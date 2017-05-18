from django.test import TestCase
from unittest.mock import Mock

from .models import Annotation, Tag


class TestAnnotation(TestCase):

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

    def test_info(self):
        annotation = Annotation.objects.create()
        # tags should be an empty list when none are set
        assert not annotation.info()['tags']
        tags = ['manicule', 'dash']
        annotation.handle_extra_data({'tags': tags}, Mock())
        # order not guaranteed / not important; sort for comparison
        assert annotation.info()['tags'].sort() == tags.sort()


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
