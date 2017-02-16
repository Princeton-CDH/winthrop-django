import requests


class ViafAPI(object):
    """Wrapper for VIAF API.

    https://platform.worldcat.org/api-explorer/apis/VIAF
    """

    # NOTE: API urls use www prefix, but VIAF URIs do not

    #: base url for VIAF API methods
    api_base = "https://www.viaf.org/viaf"
    #: base url for VIAF URIs
    uri_base = "https://viaf.org/viaf"

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
        return "%s/%s/" % (cls.uri_base, viaf_id)
