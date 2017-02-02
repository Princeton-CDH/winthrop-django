import re
from django.http import HttpResponse, JsonResponse
from dal import autocomplete

from .viaf import ViafAPI


class ViafLookup(autocomplete.Select2ListView):

    def _parse_dates(term_string):
        """Parses date possibilities from VIAF term field"""
        # This finds numbers for grabbing dates if they exist
        date_re = r"\d+"
        results = re.findall(date_re, term_string)
        date_list = []
        try:
            date_list.append(results[0])
        except IndexError:
            date_list.append('')
        
        try:
            date_list.append(results[1])
        except IndexError:
            date_list.append('')


    def get(self, request, *args, **kwargs):
        """"Return JSON with parsed fields for Person model."""
        v = ViafAPI()
        result = v.search(self.q)
        if result:
            results = result["result"]
            # VIAF is inconsistent on date formatting for approx.
            # This re catches the pattern for both ca and approximately
            name_re = r"^.+?(?=\W\s\d|\W\sca|\W\sapproximately)"
            return JsonResponse({
                results: [dict(
                    authorized_name=re.findall(name_re, term['term'])[0],
                    viaf_id=v.uri_from_id(term['viafid']),
                    birth=(_parse_dates(term['term'])[0]),
                    death=(_parse_dates(term['term'])[1]),
                 ) for term in results],
            })

        return HttpResponse("VIAF Lookup Failed")
    
    def get_label(self, item):

