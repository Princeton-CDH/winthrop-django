from datetime import datetime

from dal import autocomplete
from django.db.models import Q
from django.views.generic import ListView, DetailView
from djiffy.models import Canvas

from winthrop.books.models import Book, Publisher, Language, Subject
from winthrop.common.solr import PagedSolrQuery
from winthrop.common.views import LastModifiedListMixin


class BookListView(ListView, LastModifiedListMixin):
    model = Book
    template_name = 'books/book_list.html'
    paginate_by = 50

    def solr_query_opts(self):
        return {
            'q': '*:*',
            'sort': 'last_modified desc',
            'fq': 'content_type:(%s)' % str(Book._meta)
        }

    def get_queryset(self, **kwargs):
        # return all books, filtering on content type
        return PagedSolrQuery(self.solr_query_opts())

    def last_modified(self):
        '''override last modified logic to work with Solr'''
        query_opts = self.solr_query_opts()
        # override sort to return most recent modification date,
        # only return last modified value and nothing else
        query_opts.update({
            'sort': 'last_modified desc',
            'fl': 'last_modified'
        })

        psq = PagedSolrQuery(query_opts)
        if psq.count():
            # Solr stores date in isoformat; convert to datetime
            return datetime.strptime(psq[0]['last_modified'], '%Y-%m-%dT%H:%M:%S.%fZ')


class BookDetailView(DetailView):
    model = Book



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
