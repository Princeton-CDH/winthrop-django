from django.test import TestCase
from .models import Annotation, Tag


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
