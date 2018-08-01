from django import forms
from django.test import TestCase

from winthrop.books.forms import RadioSelectWithDisabled, SearchForm, \
    RangeWidget, RangeField


class TestRadioWithDisabled(TestCase):
    # NOTE: copied as-is from PPA

    def setUp(self):

        class TestForm(forms.Form):
            '''Build a test form use the widget'''
            CHOICES = (
                ('no', {'label': 'no select', 'disabled': True}),
                ('yes', 'yes can select'),
            )

            yes_no = forms.ChoiceField(choices=CHOICES,
                widget=RadioSelectWithDisabled)

        self.form = TestForm()

    def test_create_option(self):

        rendered = self.form.as_p()
        # no is disabled
        self.assertInHTML('<input type="radio" name="yes_no" value="no" '
                          'required id="id_yes_no_0" disabled="disabled" />',
                          rendered)
        # yes is not disabled
        self.assertInHTML('<input type="radio" name="yes_no" value="yes" '
                          'required id="id_yes_no_1" />', rendered)


class TestSearchForm(TestCase):

    def test_init(self):
        searchform = SearchForm({})
        # no fields required
        assert searchform.is_valid()
        # relevance sort disabled
        assert searchform.fields['sort'].widget.choices[-1][1]['disabled']

        # relevance sort not disabled when keyword search is present
        searchform = SearchForm({'query': 'astronomiae'})
        # label only, no widget options to set as disabled
        assert searchform.fields['sort'].widget.choices[-1][1] == 'Relevance'

    def test_get_solr_sort_field(self):
        form = SearchForm()
        assert form.get_solr_sort_field('relevance') == \
            form.solr_sort_fields['relevance']
        assert form.get_solr_sort_field('author_asc') == \
            form.solr_sort_fields['author_asc']


def test_range_widget():
    # range widget decompress logic
    assert RangeWidget().decompress('') == [None, None]
    # not sure how it actually handles missing inputs...
    # assert RangeWidget().decompress('100-') == [100, None]
    # assert RangeWidget().decompress('-250') == [None, 250]
    assert RangeWidget().decompress('100-250') == [100, 250]


def test_range_field():
    # range widget decompress logic
    assert RangeField().compress([]) == ''
    assert RangeField().compress([100, None]) == '100-'
    assert RangeField().compress([None, 250]) == '-250'
    assert RangeField().compress([100, 250]) == '100-250'
