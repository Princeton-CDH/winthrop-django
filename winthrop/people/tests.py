import json

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
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
        assert result is None

    def test_get_uri(self):
        assert ViafAPI.uri_from_id('1234') == \
            'https://viaf.org/viaf/1234/'


class TestViafAutoSuggest(TestCase):
    
    def setUp(self):
        # create an admin user to test autocomplete views
        # based on code for winthrop.places.tests
        self.password = 'pass!@#$'
        self.admin = get_user_model().objects.create_superuser(
            'testadmin',
            'test@example.com',
            self.password
        ) 

    @patch('winthrop.people.views.ViafAPI')
    def test_viaf_autosuggest(self, mockviafapi):
        viaf_autosuggest_url = reverse('people:viaf-autosuggest')
        result = self.client.get(viaf_autosuggest_url,
            params={'q': 'austen'})
        # not allowed to anonymous user
        assert result.status_code == 302

        self.client.login(username=self.admin.username, password=self.password)

        # Sample of the dict passed by the api
        mock_response = [{
            'displayForm': 'Austen, Jane, 1775-1817',
            'term': 'Austen, Jane, 1775-1817',
            'viafid': '102333412'
        }]    

        mockviafapi.return_value.suggest.return_value = mock_response
        # Get the actual URL from the API 
        mockviafapi.return_value.uri_from_id = ViafAPI.uri_from_id

        # Check that a logged in user can get the page
        result = self.client.get(viaf_autosuggest_url, {'q': 'austen'})
        assert result.status_code == 200
        # Pull the JSON response in and break it down
        assert isinstance(result, JsonResponse)
        data = json.loads(result.content.decode('utf-8'))
        # Should be a list with at least one dictionary, if actual result
        assert isinstance(data['results'], list)
        assert isinstance(data['results'][0], dict)
        # Now check for what needs to be in a dict to fill the autocomplete
        data = data['results'][0]
        assert data['id'] == 'https://viaf.org/viaf/102333412/'
        assert data['text'] == 'Austen, Jane, 1775-1817'

