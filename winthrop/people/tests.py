import json
import os
import requests

from django.test import TestCase, override_settings
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.urls import reverse
from unittest.mock import patch

from winthrop.places.models import Place
from .models import Person, Residence, RelationshipType, Relationship
from .viaf import ViafAPI
from rdflib import Graph

# Get the fixtures dir for this app
FIXTURES_PATH = os.path.join(settings.BASE_DIR, 'winthrop/people/fixtures')


class TestPerson(TestCase):
    def setUp(self):
        """Load the sample XML file and pass to the TestCase object"""
        fixture_file = os.path.join(FIXTURES_PATH, 'sample_viaf_rdf.xml')
        with open(fixture_file, 'r') as fixture:
            self.mock_rdf = fixture.read()

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

    @patch('winthrop.people.viaf.ViafAPI.get_RDF',
        return_value=Graph().serialize())
    @patch('winthrop.people.viaf.ViafAPI.get_years', return_value=(1800, 1900))
    def test_viaf_dates(self, fakedrdf, fakedyears):
        '''Check that if a viaf_id is set, save method will call ViafAPI'''
        pers = Person.objects.create(authorized_name='Mr. X',
            viaf_id='http://notviaf/viaf/0000/')
        assert pers.birth == 1800
        assert pers.death == 1900

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

    def setUp(self):
        '''Build a test relationship for use'''
        father = Person(authorized_name='Joe Schmoe')
        son = Person(authorized_name='Joe Schmoe Jr.')
        parent = RelationshipType(name='parent')

        father.save()
        son.save()
        parent.save()

        rel = Relationship(from_person=father, to_person=son,
            relationship_type=parent)
        rel.save()

    def test_str(self):
        rel = Relationship.objects.get(pk=1)
        assert str(rel) == 'Joe Schmoe parent Joe Schmoe Jr.'

    def test_through_relationships(self):
        '''Make sure from/to sets make sense and follow consistent naming'''
        father = Person.objects.get(pk=1)
        son = Person.objects.get(pk=2)

        # Not reciprocal, so from_relationships but not to_relationships
        query = father.from_relationships.all()
        assert isinstance(query[0], Relationship)
        assert query[0].from_person == father
        assert query[0].to_person == son

        query = father.to_relationships.all()
        assert not query

        # Check non-reciprocity, from and to person are same for the
        # Relationship object
        query = son.to_relationships.all()
        assert isinstance(query[0], Relationship)
        assert query[0].from_person == father
        assert query[0].to_person == son

        query = son.from_relationships.all()
        assert not query


class TestViafAPI(TestCase):

    def setUp(self):
        """Load the sample XML file and pass to the TestCase object"""
        fixture_file = os.path.join(FIXTURES_PATH, 'sample_viaf_rdf.xml')
        with open(fixture_file, 'r') as fixture:
            self.mock_rdf = fixture.read()

        graph = Graph()
        self.empty_rdf = graph.serialize()

    @patch('winthrop.people.viaf.requests')
    def test_suggest(self, mockrequests):
        viaf = ViafAPI()
        mockrequests.codes = requests.codes
        # Check that query with no matches still returns an empty list
        mock_result = {'query': 'notanauthor', 'result': None}
        mockrequests.get.return_value.status_code = requests.codes.ok
        mockrequests.get.return_value.json.return_value = mock_result
        assert viaf.suggest('notanauthor') == []
        mockrequests.get.assert_called_with(
            'https://www.viaf.org/viaf/AutoSuggest',
            params={'query': 'notanauthor'})

        # valid (abbreviated) response
        mock_result['result'] = [{
          "term": "Austen, Jane, 1775-1817",
          "displayForm": "Austen, Jane, 1775-1817",
          "recordID": "102333412"
        }]
        mockrequests.get.return_value.json.return_value = mock_result
        assert viaf.suggest('austen') == mock_result['result']

        # bad status code on the response - should still return an empty list
        mockrequests.get.return_value.status_code = requests.codes.forbidden
        assert viaf.suggest('test') == []

    def test_get_uri(self):
        assert ViafAPI.uri_from_id('1234') == \
            'https://viaf.org/viaf/1234/'
        # numeric id should also work
        assert ViafAPI.uri_from_id(1234) == \
            'https://viaf.org/viaf/1234/'

    @patch('winthrop.people.viaf.requests')
    def test_getRDF(self, mockrequests):
        viaf = ViafAPI()
        mock_rdf = self.mock_rdf
        empty_rdf = self.empty_rdf
        mockrequests.codes = requests.codes

        # Mock a GET that works correctly
        mockrequests.get.return_value.status_code = requests.codes.ok
        mockrequests.get.return_value.text = mock_rdf
        assert viaf.get_RDF('89599270') == mock_rdf

        # Mock a GET that returns a bad code
        mockrequests.get.return_value.status_code = requests.codes.bad
        assert viaf.get_RDF('89599270') == empty_rdf

    def test_get_years(self):
        viaf = ViafAPI()
        mock_rdf = self.mock_rdf
        empty_rdf = self.empty_rdf

        # Test fixture should produce a tuple as follows
        assert viaf.get_years(mock_rdf) == (69, 140)
        # An empty RDF should produce (None, None)
        assert viaf.get_years(empty_rdf) == (None, None)

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
            'viafid': '102333412',
            'nametype': 'personal',
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

class TestPersonViews(TestCase):
    fixtures = ['sample_book_data.json']

    def setUp(self):
        # create an admin user to test autocomplete views
        self.password = 'pass!@#$'
        self.admin = get_user_model().objects.create_superuser('testadmin',
            'test@example.com', self.password)

    def test_person_autocomplete(self):
        pub_autocomplete_url = reverse('people:autocomplete')
        result = self.client.get(pub_autocomplete_url,
            params={'q': 'Abelin'})
        # not allowed to anonymous user
        assert result.status_code == 302

        # login as an admin user
        self.client.login(username=self.admin.username, password=self.password)

        result = self.client.get(pub_autocomplete_url, {'q': 'Abelin'})
        assert result.status_code == 200
        # decode response to inspect
        data = json.loads(result.content.decode('utf-8'))
        assert data['results'][0]['text'] == 'Abelin, Johann Philipp'

        # Now set the winthrop flag and make a Winthrop to test
        Person.objects.create(authorized_name='Winthrop, Abigail')
        Person.objects.create(authorized_name='Winthrop, Thomas')

        result = self.client.get(pub_autocomplete_url,
            {'q': 'A', 'winthrop': True})
        # Forming this as an actual query string so that the behavior mimes
        # the additional query string value passed by the author autocomplete
        data = json.loads(result.content.decode('utf-8'))
        assert data['results'][0]['text'] == 'Winthrop, Abigail'
        # Further check that it sorts by authorized_name as per the default
        assert data['results'][1]['text'] == 'Winthrop, Thomas'
        # And then as normal
        assert data['results'][2]['text'] == 'Abelin, Johann Philipp'
