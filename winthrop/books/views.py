from django.db.models import Q
from dal import autocomplete
from djiffy.models import Canvas

from .models import Publisher


class PublisherAutocomplete(autocomplete.Select2QuerySetView):
    # basic publisher autocomplete lookup, based on
    # django-autocomplete-light tutorial
    # restricted to staff only in url config

    def get_queryset(self):
        return Publisher.objects.filter(name__icontains=self.q)


class CanvasAutocomplete(autocomplete.Select2QuerySetView):
    # basic publisher autocomplete lookup, based on
    # django-autocomplete-light tutorial
    # restricted to staff only in url config

    def get_queryset(self):
        return Canvas.objects.filter(
            Q(name__icontains=self.q) |
            Q(uri__contains=self.q)
        )
