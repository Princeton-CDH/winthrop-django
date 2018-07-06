from dal import autocomplete
from django.core.validators import ValidationError
from django.db.models import Q
from django.views.generic import ListView, DetailView
from djiffy.models import Canvas
from SolrClient.exceptions import SolrError

from winthrop.books.models import Book, Publisher, Language, Subject
from winthrop.books.forms import SearchForm
from winthrop.common.solr import PagedSolrQuery
from winthrop.common.views import LastModifiedListMixin, LastModifiedMixin


class BookListView(ListView, LastModifiedListMixin):
    model = Book
    template_name = 'books/book_list.html'
    paginate_by = 50
    form_class = SearchForm
    form = None

    def solr_query_opts(self):
        # NOTE: solr query logic used by both the view and to generate
        # last-modified value for header/conditional display

        form_opts = self.request.GET.copy()

        # NOTE: default sort logic borrowed from PPA
        # if relevance sort is requested but there is no keyword search
        # term present, clear it out and fallback to default sort
        if not 'query' in form_opts and 'sort' in form_opts and \
          form_opts['sort'] == 'relevance':
            del form_opts['sort']

        for key, val in self.form_class.defaults.items():
            # set as list to avoid nested lists
            # follows solution using in derrida-django for InstanceListView
            if isinstance(val, list):
                form_opts.setlistdefault(key, val)
            else:
                form_opts.setdefault(key, val)

        self.form = self.form_class(form_opts)
        # if the form is not valid, bail out
        if not self.form.is_valid():
            raise ValidationError('Search form is not valid')

        search_opts = {}
        if self.form.is_valid():
            search_opts = self.form.cleaned_data

        query = search_opts.get("query", None)

        solr_q = '*:*'
        # fields = '*'
        if query:
            solr_q = 'text:(%s)' % query
            # NOTE: score is needed in field list if we want to
            # display it for debugging solr indexing
            # fields = '*,score'

        solr_sort = 'last_modified desc'
        sort = search_opts.get("sort", None)

        if sort:
            solr_sort = self.form.get_solr_sort_field(sort)

        return {
            'q': solr_q,
            'sort': solr_sort,
            # 'fl': fields,
            'fq': 'content_type:(%s)' % Book.content_type()
        }

    def get_queryset(self, **kwargs):
        # return all books, filtering on content type
        try:
            return PagedSolrQuery(self.solr_query_opts())
        except ValidationError:
            # if the form is not valid, return an empty queryset and bail out
            # (queryset needed for django paginator)
            return Book.objects.none()

    def get_context_data(self, **kwargs):
        try:
            # catch an error querying solr when the search terms cannot be parsed
            # (e.g., incomplete exact phrase)
            context = super().get_context_data(**kwargs)

        except SolrError as solr_err:
            context = {'object_list': []}
            if 'Cannot parse' in str(solr_err):
                error_msg = 'Unable to parse search query; please revise and try again.'
            else:
                # NOTE: this error should possibly be raised; 500 error?
                error_msg = 'Something went wrong.'
            context['error'] = error_msg

        context.update({
            'search_form': self.form,
        })
        return context

    def last_modified(self):
        '''override last modified logic to work with Solr'''
        try:
            query_opts = self.solr_query_opts()
        except ValidationError:
            return

        # override sort to return most recent modification date,
        # only return last modified value and nothing else
        query_opts.update({
            'sort': 'last_modified desc',
            'fl': 'last_modified'
        })

        # if a syntax or other solr error happens, no date to return
        try:
            psq = PagedSolrQuery(query_opts)
            if psq.count():
                # Solr stores date in isoformat; convert to datetime
                return self.solr_timestamp_to_datetime(psq[0]['last_modified'])
        except SolrError:
            pass


class BookDetailView(DetailView, LastModifiedMixin):
    model = Book

    def last_modified(self):
        '''book model doesn't track update; get last index modification from Solr instead'''

        # if there is a solr error, skip last-modified behavior and display page
        try:
            psq = PagedSolrQuery({
                'q': 'id:"%s"' % self.object.index_id(),
                'fl': 'last_modified'
            })
            if psq.count():
                # Solr stores date in isoformat; convert to datetime
                return self.solr_timestamp_to_datetime(psq[0]['last_modified'])
        except SolrError:
            pass



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
