from django.test import TestCase

from .models import Named

class TestNamed(TestCase):

    def test_str(self):
        named_obj = Named(name='foo')
        assert str(named_obj) == 'foo'


# currently no custom logic for Notable model to test here