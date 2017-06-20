import re
import requests
from django.utils.functional import cached_property
import rdflib

from rdflib.graph import Graph
from .namespaces import SCHEMA


class ViafAPI(object):
    """Wrapper for VIAF API.

    https://platform.worldcat.org/api-explorer/apis/VIAF
    """

    # NOTE: API urls use www prefix, but VIAF URIs do not

    #: base url for VIAF API methods
    api_base = "https://www.viaf.org/viaf"
    #: base url for VIAF URIs
    uri_base = "http://viaf.org/viaf"

    def suggest(self, query):
        """Get VIAF suggestions for the specified query string.
        For ease of processing, returns an empty list if no suggestions
        are found or something goes wrong."""
        url = '/'.join([self.api_base, 'AutoSuggest'])
        resp = requests.get(url, params={'query': query})
        # NOTE: could consider adding logging here if we find
        # we are getting lots of unexpected errors
        if resp.status_code == requests.codes.ok:
            return resp.json().get('result', None) or []
        return []

    @classmethod
    def uri_from_id(cls, viaf_id):
        """Generate a VIAF URI for the specified id"""
        return "%s/%s" % (cls.uri_base, viaf_id)


class ViafEntity(object):
    '''Object for working with a single VIAF entity.

    :param viaf_id: viaf identifier (either integer or uri)
    '''
    def __init__(self, viaf_id):
        try:
            int(viaf_id)
            self.uri = ViafAPI.uri_from_id(viaf_id)
        except ValueError:
            # NOTE: do we need to canonicalize the URI in any way to
            # ensure RDF queries work properly?
            self.uri = viaf_id

    @property
    def uriref(self):
        '''VIAF URI reference as instance of :class:`rdflib.URIRef`'''
        return rdflib.URIRef(self.uri)

    @cached_property
    def rdf(self):
        '''VIAF data for this entity as :class:`rdflib.Graph`'''
        graph = rdflib.Graph()
        graph.parse(self.uri)
        return graph

    # person-specific properties

    @property
    def birthdate(self):
        '''schema birthdate as :class:`rdflib.Literal`'''
        return self.rdf.value(self.uriref, SCHEMA.birthDate)

    @property
    def deathdate(self):
        '''schema deathdate as :class:`rdflib.Literal`'''
        return self.rdf.value(self.uriref, SCHEMA.deathDate)

    @property
    def birthyear(self):
        '''birth year'''
        if self.birthdate:
            return self.year_from_isodate(str(self.birthdate))

    @property
    def deathyear(self):
        '''death year'''
        if self.deathdate:
            return self.year_from_isodate(str(self.deathdate))

    # utility method for date parsing
    @classmethod
    def year_from_isodate(cls, date):
        '''Return just the year portion of an ISO8601 date.  Expects
        a string, returns an integer'''
        return int(date.split('-')[0])
