from django.http import JsonResponse
from dal import autocomplete
from .models import Person
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
        winthrop_search = self.request.GET.get('winthrop', None)
        if winthrop_search:
            return Person.objects.annotate(
                is_winthrop=Case(
                    When(authorized_name__icontains='Winthrop'),
                    then=Value(True),
                    default=Value(False),
                    output_field=BooleanField()
                )
            ).filter(authorized_name__icontains=self.q).order_by('is_winthrop',
                'authorized_name')

        return Person.objects.filter(authorized_name__icontains=self.q)
