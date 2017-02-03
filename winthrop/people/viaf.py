import json
import requests


class ViafAPI(object):
    """Wrapper for Viaf API, results dict options for making JSON strings"""

    def __init__(self):
        self.base_url = "https://www.viaf.org/"

    def suggest(self, query):
        """Do a GET request to pull in JSON"""
        url = self.base_url + "viaf/AutoSuggest?query="
        r = requests.get("%s%s" % (url, query))
        return (r.json())['result']

    @classmethod
    def uri_from_id(cls, viaf_id):
        return "https://viaf.org/viaf/%s/" % viaf_id
