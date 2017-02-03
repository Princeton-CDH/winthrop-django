import json
import requests


class ViafAPI(object):
    """Wrapper for Viaf API"""

    def __init__(self):
        self.base_url = "https://www.viaf.org/"

    def suggest(self, query):
        """Do a GET request to pull in JSON"""
        url = self.base_url + "viaf/AutoSuggest?query="
        r = requests.get("%s%s" % (url, query))
        # If result is empty, return an empty list instead of None
        if not (r.json())['result']:
            return json.dumps({'result': []})

        return r.json()

    @classmethod
    def uri_from_id(cls, viaf_id):
        return "https://viaf.org/viaf/%s/" % viaf_id
