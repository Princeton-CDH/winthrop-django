import re
from django.http import HttpResponse, JsonResponse
from dal import autocomplete

from .viaf import ViafAPI


class ViafAutoSuggest(autocomplete.Select2ListView):
    """ View to provide DAL JSON info"""
    @classmethod
    def _parse_dates(cls, displayForm_string):
        """Parses date possibilities from VIAF displayForm field"""
        # This finds numbers for grabbing dates if they exist
        date_re = r"\d+"
        results = re.findall(date_re, displayForm_string)
        date_list = []
        try:
            date_list.append(results[0])
        except IndexError:
            date_list.append('')
        try:
            date_list.append(results[1])
        except IndexError:
            date_list.append('')
        return date_list

    @classmethod
    def _parse_name(cls, displayForm_string):
        """Parses name from displayForm field"""
        # VIAF is inconsistent on date formatting for approx.
        # This re catches the pattern for both ca and approximately
        name_re = r"^.+?(?=$|\W\s\d|\W\sca|\W\sapproximately)"
        name = re.search(name_re, displayForm_string)
        return name.group(0)

    def get(self, request, *args, **kwargs):
        """Return JSON with parsed fields for Person model."""
        v = ViafAPI()
        result = v.suggest(self.q)
        if result:
            return JsonResponse({
                'results': [dict(
                    authorized_name=(self._parse_name(item['displayForm'])),
                    id=v.uri_from_id(item['viafid']),
                    birth=(self._parse_dates(item['displayForm'])[0]),
                    death=(self._parse_dates(item['displayForm'])[1]),
                    text=item['displayForm'], 
                ) for item in result],
            })
        else:
            # Return an empty list in case the search returns null
            return JsonResponse({'results': []})
   
    def get_label(self, item):
        return item['displayForm']

