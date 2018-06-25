import json
import os
import requests
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.urls import reverse
from django.utils import safestring
import rdflib

from winthrop.books.models import Book, PersonBook, PersonBookRelationshipType
from winthrop.places.models import Place
from .models import Person, Residence, RelationshipType, Relationship
from .viaf import ViafAPI, ViafEntity
from .admin import ViafWidget


# Get the fixtures dir for this app
FIXTURES_PATH = os.path.join(settings.BASE_DIR, 'winthrop', 'people', 'fixtures')


class TestPerson(TestCase):

    fixture_file = os.path.join(FIXTURES_PATH, 'sample_viaf_rdf.xml')

    def setUp(self):
        """Load the sample XML file and pass to the TestCase object"""
        with open(self.fixture_file, 'r') as fixture:
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

    def test_viaf(self):
        uri = 'http://viaf.org/89599270'
        pers = Person(viaf_id=uri)
        assert isinstance(pers.viaf, ViafEntity)
        assert pers.viaf.uri == uri

    def test_set_birth_death_years(self):
        # use viaf id matching fixture rdf file
        pers = Person(viaf_id='http://viaf.org/viaf/89599270')

        # patch fixture in for viaf rdf
        test_rdf = rdflib.Graph()
        test_rdf.parse(self.fixture_file)

        with patch('winthrop.people.viaf.rdflib.Graph') as mockgraph:
            # patch parse to avoid trying to parse live uri
            mockgraph.return_value = test_rdf

            with patch.object(test_rdf, 'parse'):
                pers.set_birth_death_years()
                assert pers.birth == pers.viaf.birthyear
                assert pers.birth == 69
                assert pers.death == pers.viaf.deathyear
                assert pers.death == 140

    def test_save(self):
        pers = Person()
        # test that birth/death years are set from viaf when appropriate
        with patch.object(pers, 'set_birth_death_years') as mocksetyears:
            # no viaf id - not called
            pers.save()
            mocksetyears.assert_not_called()

            # viaf id but birth/death already set - not called
            pers.viaf_id = 'http://viaf.org/viaf/89599270'
            pers.birth = 100
            pers.death = 150
            pers.save()
            mocksetyears.assert_not_called()

            # viaf id but birth already set - not called
            pers.viaf_id = 'http://viaf.org/viaf/89599270'
            pers.birth = 2001
            pers.death = None
            pers.save()
            mocksetyears.assert_not_called()


            # viaf id and no birth/death - called
            pers.viaf_id = 'http://viaf.org/viaf/89599270'
            pers.birth = None
            pers.death = None
            pers.save()
            mocksetyears.assert_called_with()

    def test_authorized_name_changed(self):
        person = Person(authorized_name='John Jacob Jingleheimer Smith')
        assert not person.authorized_name_changed
        # change the name
        person.authorized_name = 'JJ Smith'
        assert person.authorized_name_changed
        # save changes; should no longer be marked as changed
        person.save()
        assert not person.authorized_name_changed


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
        assert '%s %s (1900-)' % (self.person, self.place)


class TestRelationshipType(TestCase):

    def test_str(self):
        rel_type = RelationshipType(name='parent')
        assert str(rel_type) == 'parent'


class TestRelationship(TestCase):

    def setUp(self):
        '''Build a test relationship for use'''
        father = Person(authorized_name='Joe Schmoe')
        son = Person(authorized_name='Joe Schmoe Jr.')
        parent, created = RelationshipType.objects.get_or_create(name='Parent')

        father.save()
        son.save()

        rel = Relationship(from_person=father, to_person=son,
            relationship_type=parent)
        rel.save()

    def test_str(self):
        rel = Relationship.objects.all().first()
        assert str(rel) == 'Joe Schmoe Parent Joe Schmoe Jr.'

    def test_through_relationships(self):
        '''Make sure from/to sets make sense and follow consistent naming'''
        father = Person.objects.get(authorized_name='Joe Schmoe')
        son = Person.objects.get(authorized_name='Joe Schmoe Jr.')

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

        graph = rdflib.Graph()
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
            'http://viaf.org/viaf/1234'
        # numeric id should also work
        assert ViafAPI.uri_from_id(1234) == \
            'http://viaf.org/viaf/1234'


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
        assert data['id'] == 'http://viaf.org/viaf/102333412'
        assert data['text'] == 'Austen, Jane, 1775-1817'

        # test that non-personal names are filtered out
        mock_response = [{
            "term": "Jersey",
            "displayForm": "Jersey",
            "nametype": "geographic",
            "lc": "n79086822",
            "dnb": "000438200",
            "selibr": "149410",
            "bne": "xx5289012",
            "viafid": "142485803",
            "score": "2567",
            "recordID": "142485803"
        }]
        mockviafapi.return_value.suggest.return_value = mock_response
        result = self.client.get(viaf_autosuggest_url, {'q': 'jersey'})
        # should return an empty list because no personal names were returned
        data = json.loads(result.content.decode('utf-8'))
        assert not data['results']


class TestViafEntity(TestCase):

    test_id = 102333412
    test_uri = 'http://viaf.org/viaf/102333412'
    rdf_fixture = os.path.join(FIXTURES_PATH, 'sample_viaf_rdf.xml')

    def test_init(self):
        # numeric id (either int or string should work)
        ent = ViafEntity(self.test_id)
        assert ent.uri == self.test_uri
        ent = ViafEntity(str(self.test_id))
        assert ent.uri == self.test_uri
        # uri
        ent = ViafEntity(self.test_uri)
        assert ent.uri == self.test_uri

    def test_uriref(self):
        ent = ViafEntity(self.test_uri)
        assert ent.uriref == rdflib.URIRef(self.test_uri)

    @patch('winthrop.people.viaf.rdflib')
    def test_rdf(self, mockrdflib):
        ent = ViafEntity(self.test_uri)
        assert ent.rdf == mockrdflib.Graph.return_value
        # should initialize a graph and parse uri data
        mockrdflib.Graph.assert_called_with()
        mockrdflib.Graph.return_value.parse.assert_called_with(
            self.test_uri)

    def test_properties(self):
        # use viaf id matching fixture rdf file
        test_rdf = rdflib.Graph()
        test_rdf.parse(self.rdf_fixture)

        with patch('winthrop.people.viaf.rdflib.Graph') as mockgraph:
            mockgraph.return_value = test_rdf
            # patch parse to avoid trying to parse live uri
            with patch.object(test_rdf, 'parse') as mockparse:
                ent = ViafEntity('89599270')
                assert ent.birthyear == 69
                assert ent.deathyear == 140

                mockparse.assert_called_once_with(ent.uri)

    def test_year_from_isodate(self):
        assert ViafEntity.year_from_isodate('2001') == 2001
        assert ViafEntity.year_from_isodate('2002-01') == 2002
        assert ViafEntity.year_from_isodate('2004-03-05') == 2004


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

        # Forming this as an actual query string so that the behavior mimes
        # the additional query string value passed by the author autocomplete
        laski = Person.objects.get(authorized_name__icontains='Jan')
        PersonBook.objects.create(book=Book.objects.get(pk=1), person=laski,
            relationship_type=PersonBookRelationshipType.objects.get(pk=1))
        annotator_url = reverse('people:autocomplete', args=['annotator'])
        result = self.client.get(annotator_url, {'q': 'Jan'})
        data = json.loads(result.content.decode('utf-8'))
        # Jan should be listed but Abelin shouldn't even be listed
        assert data['results'][0]['text'] == laski.authorized_name
        assert len(data['results']) == 1


class TestViafWidget(TestCase):

    def test_render(self):
        widget = ViafWidget()
        # no value set - should not error
        rendered = widget.render('person', None, {'id': 123})
        assert '<p><br /><a id="viaf_uri" target="_blank" href=""></a></p>' \
            in rendered
        # rendered widget includes help text
        assert 'will automatically set the birth' in rendered
        # test marked as "safe"?

        # uri value set - should be included in generated link
        uri = 'http://viaf.org/viaf/13103985/'
        rendered = widget.render('person', uri, {'id': 1234})
        assert '<a id="viaf_uri" target="_blank" href="%(uri)s">%(uri)s</a>' \
            % {'uri': uri} in rendered
