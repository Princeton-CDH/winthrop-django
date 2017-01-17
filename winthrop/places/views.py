from django.shortcuts import render
from dal import autocomplete

from .models import Place


class PlaceAutocomplete(autocomplete.Select2QuerySetView):
    # basic place autocomplete lookup, based on
    # django-autocomplete-light tutorial
    # restricted to staff only in url config

    def get_queryset(self):
        return Place.objects.filter(name__istartswith=self.q)
