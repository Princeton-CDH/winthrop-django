from django.test import TestCase, override_settings
from django.urls import reverse
from unittest.mock import patch

from winthrop.places.models import Place
from .models import Person, Residence, RelationshipType, Relationship
from .viaf import ViafAPI


class TestPerson(TestCase):

    def test_str(self):
        pers = Person(authorized_name='Mr. So and So')
        assert str(pers) == 'Mr. So and So'

    def test_dates(self):
        pers = Person.objects.create(authorized_name='Mr. So', birth=1800,
            death=1845)
        # alias fields and actual date range fields should both be set
        assert pers.birth == 1800
        assert pers.start_year == 1800
        assert pers.death == 1845
        assert pers.end_year == 1845

        # queryset filters on alias fields should also work
        assert Person.objects.get(birth=1800) == pers

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


class TestViafAPI(TestCase):

    def test_init(self):
        v = ViafAPI()
        # It should know the base url
        assert v.base_url == 'https://www.viaf.org/'

    @patch('winthrop.people.viaf.requests')
    def test_suggest(self, mockrequests):
        v = ViafAPI()
        # Check that query to no author works to check JSON forwarding
        mock_result = {'query': 'notanauthor', 'result': None}
        mockrequests.get.return_value.json.return_value = mock_result
        result = v.suggest('notanauthor')
        assert result == None 
