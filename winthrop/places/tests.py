from django.test import TestCase
import pytest

from .models import Place


@pytest.mark.django_db
class TestPlace(TestCase):

    def test_str(self):
        pl = Place(name='New York', geonames_id='12345')
        assert str(pl) == 'New York'
