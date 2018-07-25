from django import forms
from django.utils.safestring import mark_safe
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db.models import Max, Min

from winthrop.books.models import Book


## Disabled input logic borrowed from PPA (ppa.archive.forms)
class SelectDisabledMixin(object):
    '''
    Mixin for :class:`django.forms.RadioSelect` or :class:`django.forms.CheckboxSelect`
    classes to set an option as disabled. To disable, the widget's choice
    label option should be passed in as a dictionary with `disabled` set
    to True::

        {'label': 'option', 'disabled': True}.
    '''

    # Using a solution at https://djangosnippets.org/snippets/2453/
    def create_option(self, name, value, label, selected, index, subindex=None,
                      attrs=None):
        disabled = None

        if isinstance(label, dict):
            label, disabled = label['label'], label['disabled']
        option_dict = super().create_option(
            name, value, label, selected, index,
            subindex=subindex, attrs=attrs
        )
        if disabled:
            option_dict['attrs'].update({'disabled': 'disabled'})
        return option_dict


class RadioSelectWithDisabled(SelectDisabledMixin, forms.RadioSelect):
    '''
    Subclass of :class:`django.forms.RadioSelect` with option to mark
    a choice as disabled.
    '''


class FacetChoiceField(forms.MultipleChoiceField):
    '''Add CheckboxSelectMultiple field with facets taken from solr query'''
    # Borrowed from https://github.com/Princeton-CDH/derrida-django/blob/develop/derrida/books/forms.py
    # customize multiple choice field for use with facets.
    # no other adaptations needed
    # - turn of choice validation (shouldn't fail if facets don't get loaded)
    # - default to not required
    # - use checkbox select multiple as default widget

    # TODO: maybe disable this and go back to multiselect box
    widget = forms.CheckboxSelectMultiple

    def __init__(self, *args, **kwargs):
        if 'required' not in kwargs:
            kwargs['required'] = False
        super().__init__(*args, **kwargs)

    def valid_value(self, value):
        return True


# RangeWidget and RangeField also borrowed from Derrida/PPA codebase

class RangeWidget(forms.MultiWidget):
    '''date range widget, for two numeric inputs'''

    #: separator string when splitting out values in decompress
    sep = '-'
    #: template to use to render range multiwidget
    # (based on multiwidget, but adds "to" between dates)
    template_name = 'books/widgets/rangewidget.html'

    def __init__(self, *args, **kwargs):
        widgets = [
            forms.NumberInput(),
            forms.NumberInput()
        ]
        super().__init__(widgets, *args, **kwargs)

    def decompress(self, value):
        if value:
            return [int(val) for val in value.split(self.sep)]
        return [None, None]


class RangeField(forms.MultiValueField):
    widget = RangeWidget

    def __init__(self, *args, **kwargs):
        fields = (
            forms.IntegerField(
                error_messages={'invalid': 'Enter a number'},
                validators=[
                    RegexValidator(r'^[0-9]*$', 'Enter a valid number.'),
                ],
                required=False
            ),
            forms.IntegerField(
                error_messages={'invalid': 'Enter a number'},
                validators=[
                    RegexValidator(r'^[0-9]*$', 'Enter a valid number.'),
                ],
                required=False
            ),
        )
        kwargs['fields'] = fields
        super().__init__(require_all_fields=False, *args, **kwargs)

    def compress(self, data_list):
        # if both values are set and the first is greater than the second,
        # raise a validation error
        if all(data_list) and len(data_list) == 2 and data_list[0] > data_list[1]:
            raise ValidationError('Invalid range (%s - %s)' % (data_list[0], data_list[1]))
        return self.widget.sep.join(['%d' % val if val else '' for val in data_list])


# pubdate min/max methods and range logic borrowed from PPA/Derrida codebase
class SearchForm(forms.Form):
    '''Search form for searching across :class:`~winthrop.books.models.Books`.'''

    SORT_CHOICES = [
        ('author_asc', 'Author A-Z'),
        ('author_desc', 'Author Z-A'),
        ('pub_year_asc', 'Year Oldest-Newest'),
        ('pub_year_desc', 'Year Newest-Oldest'),
        ('relevance', 'Relevance'),
    ]

    defaults = {
        'sort': 'author_asc',
    }

    query = forms.CharField(label='Keyword or Phrase', required=False)

    sort = forms.ChoiceField(widget=RadioSelectWithDisabled, choices=SORT_CHOICES,
                             required=False)

    # Solr facet choice fields
    author = FacetChoiceField()
    editor = FacetChoiceField()
    translator = FacetChoiceField()
    language = FacetChoiceField()
    subject = FacetChoiceField()
    annotator = FacetChoiceField()
    # range choice fields
    pub_year = RangeField(
        label='Publication Year',
        required=False,
        widget=RangeWidget(attrs={
            'size': 4,
            '_inline': True
        })
    )
    # map solr facet field to corresponding form input
    solr_facet_fields = {
        'author_exact': 'author',
        'editor_exact': 'editor',
        'translator_exact': 'translator',
        'language_exact': 'language',
        'subject_exact': 'subject',
        'annotator_exact': 'annotator'
    }

    # TODO: Should this be a dict? Right now it doesn't need a different name
    # to map to the fields used in the form.
    range_facets = ['pub_year']

    def __init__(self, data=None, *args, **kwargs):
        '''
        Set choices dynamically based on form kwargs and presence of keywords.
        '''
        super().__init__(data=data, *args, **kwargs)

        pubdate_range = self.pub_date_minmax()
        # because pubdate is a multifield/multiwidget, access the widgets
        # under the multiwidgets
        pubdate_widgets = self.fields['pub_year'].widget.widgets
        for idx, val in enumerate(pubdate_range):
            # don't set None as placeholder (only possible if db is empty)
            if val:
                # set placeholder and max/min values
                pubdate_widgets[idx].attrs.update({'placeholder': val,
                    'min': pubdate_range[0], 'max': pubdate_range[1]})

        # relevance is disabled unless we have a keyword query present
        if not data or not data.get('query', None):
            self.fields['sort'].widget.choices[-1] = \
                ('relevance', {'label': 'Relevance', 'disabled': True})

    def set_choices_from_facets(self, facets):
        # configure field choices based on facets returned from Solr
        # (adapted from derrida codebase)
        for facet, counts in facets.items():
            # use field from facet fields map or else field name as is
            formfield = self.solr_facet_fields.get(facet, facet)
            if formfield in self.fields:
                self.fields[formfield].choices = [
                    (val, mark_safe('%s <span>%d</span>' % (val, count)))
                    for val, count in counts.items()]

    # map form sort options to solr sort field
    solr_sort_fields = {
        'relevance': 'score desc',
        'pub_year_asc': 'pub_year asc',
        'pub_year_desc': 'pub_year desc',
        'author_asc': 'author_sort asc',
        'author_desc': 'author_sort desc',
    }

    PUBDATE_CACHE_KEY = 'book_pubdate_maxmin'

    def pub_date_minmax(self):
        '''Get minimum and maximum values for
        :class:`~winthrop.books.models.Book` publication dates
        in the database.  Used to set placeholder values for the form
        input and to generate the Solr facet range query.
        Value is cached to avoid repeatedly calculating it.
        :returns: tuple of min, max
        '''
        maxmin = cache.get(self.PUBDATE_CACHE_KEY)
        if not maxmin:
            maxmin = Book.objects \
                .aggregate(Max('pub_year'), Min('pub_year'))

            # cache as returned from django; looks like this:
            # {'pub_date__max': 1922, 'pub_date__min': 1559}

            # don't cache if values are None
            # should only happen if no data is in the db
            if all(maxmin.values()):
                cache.set(self.PUBDATE_CACHE_KEY, maxmin)

        # return just the min and max values
        return maxmin['pub_year__min'], maxmin['pub_year__max']

    def get_solr_sort_field(self, sort):
        '''
        Set solr sort fields for the query based on sort and query strings.

        :return: solr sort field
        '''
        # return solr field for requested sort option
        return self.solr_sort_fields[sort]
