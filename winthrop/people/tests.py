from django.test import TestCase
import pytest

from winthrop.places.models import Place
from .models import Person, Residence, RelationshipType, Relationship


@pytest.mark.django_db
class TestPerson(TestCase):

    def test_str(self):
        p = Person(authorized_name='Mr. So and So')
        assert str(p) == 'Mr. So and So'


@pytest.mark.django_db
class TestResidence(TestCase):

    def setUp(self):
        # test model instances to work with in tests
        self.person = Person(authorized_name='Mrs. W')
        self.place = Place(name='Podunk', geonames_id='7890')
        self.res = Residence(person=self.person, place=self.place)

    def test_dates(self):
        # no dates set
        assert '' == self.res.dates
        # date range
        self.res.start_year = 1900
        self.res.end_year = 1901
        assert '1900-1901' == self.res.dates
        # start and end dates are same year = single year
        self.res.end_year = self.res.start_year
        assert self.res.start_year == self.res.dates
        # start date but no end
        self.res.end_year = None
        assert '1900-' == self.res.dates
        # end date but no start
        self.res.end_year = 1950
        self.res.start_year = None
        assert '-1950' == self.res.dates

    def test_str(self):
        # without date
        assert '%s %s' % (self.person, self.place) == str(self.res)
        # include date if there is one
        self.res.start_year = 1900
        assert '%s %s (%s)' % (self.person, self.place, self.res.dates)


@pytest.mark.django_db
class TestRelationshipType(TestCase):

    def test_str(self):
        rel_type = RelationshipType(name='parent')
        assert str(rel_type) == 'parent'


@pytest.mark.django_db
class TestRelationship(TestCase):

    def test_str(self):
        father = Person(authorized_name='Joe Schmoe')
        son = Person(authorized_name='Joe Schmoe Jr.')
        parent = RelationshipType(name='parent')
        rel = Relationship(from_person=father, to_person=son,
            relationship_type=parent)