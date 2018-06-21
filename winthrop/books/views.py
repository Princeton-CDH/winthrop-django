from dal import autocomplete
from django.db.models import Q
from django.views.generic import ListView
from djiffy.models import Canvas

from winthrop.books.models import Book, Publisher, Language, Subject
from winthrop.common.solr import PagedSolrQuery


class BookListView(ListView):
    model = Book
    template_name = 'books/book_list.html'
    paginate_by = 50

    def get_queryset(self, **kwargs):
        # return all books, filtering on content type
        return PagedSolrQuery({
            'q': '*:*',
            'sort': 'last_modified desc',
            'fq': 'content_type:(%s)' % str(Book._meta)
        })


class PublisherAutocomplete(autocomplete.Select2QuerySetView):
    '''Basic publisher autocomplete lookup, for use with
    django-autocomplete-light.  Restricted to staff only.'''
    # NOTE staff restrection applied in url config

    def get_queryset(self):
        return Publisher.objects.filter(name__icontains=self.q)


class CanvasAutocomplete(autocomplete.Select2QuerySetView):
    '''Canvas lookup for admin interface'''
    def get_queryset(self):
        return Canvas.objects.filter(
            Q(label__icontains=self.q) |
            Q(uri__contains=self.q)
        )

class LanguageAutocomplete(autocomplete.Select2QuerySetView):
    '''Autocomplete for languages in the controlled vocabulary list'''

    def get_queryset(self):
        return Language.objects.filter(name__icontains=self.q)


class SubjectAutocomplete(autocomplete.Select2QuerySetView):
    '''Basic autocomplete view for Subjects'''
    def get_queryset(self):
        return Subject.objects.filter(name__icontains=self.q)
