from django.http import JsonResponse
from dal import autocomplete
from .models import Person
from winthrop.books.models import PersonBook
from django.db.models import BooleanField, Case, When, Value
from .viaf import ViafAPI


class ViafAutoSuggest(autocomplete.Select2ListView):
    """ View to provide VIAF suggestions for autocomplete info"""

    def get(self, request, *args, **kwargs):
        """Return JSON with suggested VIAF ids and display names."""
        viaf = ViafAPI()
        result = viaf.suggest(self.q)
        # Strip names that are not personal
        for item in result:
            if item['nametype'] is not 'personal':
                del item
        return JsonResponse({
            'results': [dict(
                id=viaf.uri_from_id(item['viafid']),
                text=(item['displayForm']),
            ) for item in result],
        })


class PersonAutocomplete(autocomplete.Select2QuerySetView):
    '''Basic person autocomplete lookup, for use with
    django-autocomplete-light.  Restricted to staff only.
    Also includes optional winthrop query string that sets whether
    to prioritize Winthrops based on search criteria in function. Can
    be extended by Q objects if necesary for more complex searches.'''
    # NOTE staff restrection applied in url config

    def get_queryset(self):
        annotator_only = ''
        if len(self.args) > 0:
            annotator_only = self.args[0]
        people = Person.objects.filter(authorized_name__icontains=self.q)
        if annotator_only == 'annotator':
                people = people.filter(personbook__isnull=False)
        return people
