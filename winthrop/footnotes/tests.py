from django.test import TestCase

from .models import SourceType, Bibliography

class TestOwningInstitution(TestCase):

    def test_item_count(self):
        src_type = SourceType.objects.first()
        assert src_type.item_count() == 0

        bibl = Bibliography.objects.create(bibliographic_note='citation',
            source_type=src_type)
        assert src_type.item_count() == 1


