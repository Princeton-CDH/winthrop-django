from django.http import JsonResponse
from dal import autocomplete

from .models import Person
from .viaf import ViafAPI


class ViafAutoSuggest(autocomplete.Select2ListView):
    """ View to provide VIAF suggestions for autocomplete info"""

    def get(self, request, *args, **kwargs):
        """Return JSON with suggested VIAF ids and display names."""
        viaf = ViafAPI()
        result = viaf.suggest(self.q)
        return JsonResponse({
            'results': [dict(
                id=viaf.uri_from_id(item['viafid']),
                text=(item['displayForm']),
            ) for item in result],
        })


class PersonAutocomplete(autocomplete.Select2QuerySetView):
    # basic person autocomplete lookup, based on
    # django-autocomplete-light tutorial
    # restricted to staff only in url config

    def get_queryset(self):
        return Person.objects.filter(authorized_name__icontains=self.q)

