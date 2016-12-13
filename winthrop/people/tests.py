from django.test import TestCase
import pytest

from winthrop.places.models import Place
from .models import Person, Residence, RelationshipType, Relationship



class TestPerson(TestCase):

    def test_str(self):
        p = Person(authorized_name='Mr. So and So')
        assert str(p) == 'Mr. So and So'


class TestResidence(TestCase):

    def setUp(self):
        # test model instances to work with in tests
        self.person = Person(authorized_name='Mrs. W')
        self.place = Place(name='Podunk', geonames_id='7890')
        self.res = Residence(person=self.person, place=self.place)

    def test_str(self):
        # without date
        assert '%s %s' % (self.person, self.place) == str(self.res)
        # include date if there is one
        self.res.start_year = 1900
        assert '%s %s (%s)' % (self.person, self.place, self.res.dates)


class TestRelationshipType(TestCase):

    def test_str(self):
        rel_type = RelationshipType(name='parent')
        assert str(rel_type) == 'parent'


class TestRelationship(TestCase):

    def test_str(self):
        father = Person(authorized_name='Joe Schmoe')
        son = Person(authorized_name='Joe Schmoe Jr.')
        parent = RelationshipType(name='parent')
        rel = Relationship(from_person=father, to_person=son,
            relationship_type=parent)