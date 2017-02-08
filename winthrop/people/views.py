import re
from django.http import HttpResponse, JsonResponse
from dal import autocomplete

from .viaf import ViafAPI


class ViafAutoSuggest(autocomplete.Select2ListView):
    """ View to provide DAL JSON info"""
    @staticmethod
    def _strip_header(string):
        '''Remove annoying headers for the text view'''
        string = re.sub(r'aus\s', '', string)
        return string

    def get(self, request, *args, **kwargs):
        """Return JSON with parsed fields for Person model."""
        v = ViafAPI()
        result = v.suggest(self.q)
        if result:
            return JsonResponse({
                'results': [dict(
                    id=v.uri_from_id(item['viafid']),
                    text=(self._strip_header(item['displayForm'])),
                ) for item in result],
            })
        else:
            # Return an empty list in case the search returns null
            return JsonResponse({'results': []})

    def get_label(self, item):
        return self._parse_name(item['displayForm'])

