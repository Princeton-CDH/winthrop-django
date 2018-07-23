from django import forms
from django.utils.safestring import mark_safe

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
    # map solr facet field to corresponding form input
    solr_facet_fields = {
        'author_exact': 'author',
        'editor_exact': 'editor',
        'translator_exact': 'translator',
        'language_exact': 'language',
        'subject_exact': 'subject',
    }

    def __init__(self, data=None, *args, **kwargs):
        '''
        Set choices dynamically based on form kwargs and presence of keywords.
        '''
        super().__init__(data=data, *args, **kwargs)

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
        'author_asc': 'author_exact asc',
        'author_desc': 'author_exact desc',
    }

    def get_solr_sort_field(self, sort):
        '''
        Set solr sort fields for the query based on sort and query strings.

        :return: solr sort field
        '''
        # return solr field for requested sort option
        return self.solr_sort_fields[sort]
