from dal import autocomplete

from .models import Publisher


class PublisherAutocomplete(autocomplete.Select2QuerySetView):
    # basic publisher autocomplete lookup, based on
    # django-autocomplete-light tutorial
    # restricted to staff only in url config

    def get_queryset(self):
        return Publisher.objects.filter(name__icontains=self.q)
