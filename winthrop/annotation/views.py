from .models import Tag
from dal import autocomplete


class TagAutocomplete(autocomplete.Select2QuerySetView):
    '''Basic autocomplete view for Tags'''
    def get_queryset(self):
        return Tag.objects.filter(name__icontains=self.q)
