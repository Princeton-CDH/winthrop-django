from dal import autocomplete
from django.core.validators import ValidationError
from django.db.models import Q
from django.http import JsonResponse
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

    def get_template_names(self):
        # when queried via ajax, return partial html for just the results section
        # (don't render the form or base template)
        if self.request.is_ajax():
            return 'books/snippets/book_list_results.html'
        return self.template_name

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

        ## faceting and filtering
        # list of filter queries; restrict to books, filter by
        # any facet fields that are specified
        # range logic adapted from PPA/Derrida projects
        range_opts = {
            'facet.range': self.form.range_facets
        }
        filter_qs = ['content_type:(%s)' % Book.content_type()]

        for range_facet in self.form.range_facets:
            # range filter requested in search options
            start = end = None
            # if start or end is specified on the form, add a filter query
            if range_facet in search_opts and search_opts[range_facet]:
                start, end = search_opts[range_facet].split('-')
                range_filter = '[%s TO %s]' % (start or '*', end or '*')
                # find works restricted by range
                filter_qs.append('%s:%s' % (range_facet, range_filter))

            # get minimum and maximum pub date values from the db
            pubmin, pubmax = self.form.pub_date_minmax()

            # NOTE: hard-coded values are fallback logic for when
            # no contents are in the database and pubmin/pubmax are None
            start = int(start) if start else pubmin or 0
            end = int(end) if end else pubmax or 1800

            # Configure range facet options specific to current field, to
            # support more than one range facet (even though not currently needed)
            range_opts.update({
                # current range filter
                'f.%s.facet.range.start' % range_facet: start,
                # NOTE: per facet.range.include documentation, default behavior
                # is to include lower bound and exclude upper bound.
                # For simplicity, increase range end by one.
                'f.%s.facet.range.end' % range_facet: end + 1,
                # calculate gap based start and end & desired number of slices
                # ideally, generate 24 slices; minimum gap size of 1
                'f.%s.facet.range.gap' % range_facet: max(1, int((end - start) / 24)),
                # restrict last range to *actual* maximum value
                'f.%s.facet.range.hardend' % range_facet: True
            })

        # check for facet filters that should be enabled
        for solr_field, form_field in self.form.solr_facet_fields.items():
            field_values = search_opts.get(form_field, None)
            if field_values:
                # Find matches for any of the terms.
                # Tag the filter using the form field name so that it
                # can be excluded when generating the facet, to get proper counts
                filter_qs.append('{!tag=%s}%s:(%s)' % \
                    (form_field, solr_field,
                     ' OR '.join('"%s"' % val for val in field_values)))

        # Construct list of facet fields to return.
        # Exclude tags based on form field name, so that counts will be
        # correct for multi-select faceting.
        # See https://lucene.apache.org/solr/guide/6_6/faceting.html#Faceting-TaggingandExcludingFilters
        # Use key to Set output label to form field name instead of solr field
        facet_fields = ['{!ex=%s key=%s}%s' % (form_field, form_field, solr_field)
                        for solr_field, form_field in self.form.solr_facet_fields.items()]

        ## sorting
        solr_sort = 'last_modified desc'
        sort = search_opts.get("sort", None)

        if sort:
            solr_sort = self.form.get_solr_sort_field(sort)

        solr_opts = {
            'q': solr_q,
            'sort': solr_sort,
            # 'fl': fields,
            # turn on faceting and add any self.form facet_fields
            'facet': 'true',
            'facet.field': facet_fields,
            'facet.limit': -1,
            # sort by alpha on facet label rather than count
            'facet.sort': 'index',
            'fq': filter_qs,
            # enabling highlighting for debugging search customization
            'hl': True,
            'hl.fl': 'text',
            'hl.snippets': 3,
            'hl.method': 'unified'
        }
        solr_opts.update(range_opts)
        return solr_opts

    def get_queryset(self, **kwargs):
        # return all books, filtering on content type
        try:
            return PagedSolrQuery(self.solr_query_opts())
        except ValidationError:
            # if the form is not valid, return an empty queryset and bail out
            # (queryset needed for django paginator)
            return Book.objects.none()

    def get_context_data(self, **kwargs):
        highlights = None
        try:
            # catch an error querying solr when the search terms cannot be parsed
            # (e.g., incomplete exact phrase)
            context = super().get_context_data(**kwargs)

            # populate form field choices based on facets
            # (may not actually be displayed except as a fallback and for testing)
            self.form.set_choices_from_facets(self.object_list.get_facets())

            # temporarily include highlights to test search index customization
            # retrieve inside try/except in case of syntax errro
            highlights = self.object_list.get_highlighting()

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
            # temporarily include highlights to test search index customization
            'highlights': highlights
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
            # Solr stores date in isoformat; convert to datetime
            return self.solr_timestamp_to_datetime(psq[0]['last_modified'])
            # skip extra call to Solr to check count and just grab the first
            # item if it exists
        except (IndexError, SolrError):
            pass


class BookFacetJSONView(BookListView):
    error_code = None

    def get_context_data(self, **kwargs):
        # skip normal context handling and only return count and facets

        # get paginator for including number of pages, but skip other
        # context data logic needed for full result view
        paginator = self.get_paginator(self.object_list, self.paginate_by)
        try:
            return {
                'total': self.object_list.count(),
                'resultsPerPage': self.paginate_by,
                'pages': paginator.num_pages,
                'facets': self.object_list.get_facets(),
                'range_facets': self.object_list.get_facets_ranges()
            }
        except SolrError as solr_err:
            error_msg = 'Something went wrong.'
            self.error_code = 500
            if 'Cannot parse' in str(solr_err):
                error_msg = ('Unable to parse search query; '
                             'please revise and try again.')
                self.error_code = 400
            return {'error': error_msg}

    def render_to_response(self, context, **response_kwargs):
        response = JsonResponse(context, **response_kwargs)
        # if something went wrong, set an error code on the response before returning
        if 'error' in context and self.error_code:
            response.status_code = self.error_code
        return response


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
