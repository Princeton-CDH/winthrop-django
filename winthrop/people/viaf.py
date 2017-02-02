import requests
from django.conf import settings


class ViafAPI(object):
    """Wrapper for ViafAPI"""

    def __init__(self):
        default_url = 'https://www.viaf.org/viaf/AutoSuggest?query='
        self.base_url = getattr(settings, "VIAF_AUTOSUGGEST_URL", default_url)

    def search(self, query):
        """Do a GET request to pull in JSON"""
        r = requests.get('%s%s' % (self.base_url, query))
        # Check to make sure we have a sucesss (i.e. a 200 code)
        if 200 <= r.status_code < 300:
            return r.json()
        else:
            return None 


