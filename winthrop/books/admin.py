from django import forms
from django.contrib import admin
from dal import autocomplete
from djiffy.admin import ManifestSelectWidget

from winthrop.common.admin import NamedNotableAdmin
from winthrop.footnotes.admin import FootnoteInline
from .models import Subject, Language, Publisher, OwningInstitution, \
    Book, Catalogue, BookSubject, BookLanguage, CreatorType, Creator, \
    PersonBook, PersonBookRelationshipType


class NamedNotableBookCount(NamedNotableAdmin):
    list_display = NamedNotableAdmin.list_display + ('book_count',)


class OwningInstitutionAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'name', 'place', 'has_notes', 'book_count')
    fields = ('name', 'short_name', 'contact_info', 'place', 'notes')
    search_fields = ('name', 'short_name', 'contact_info', 'notes')


class CollapsibleTabularInline(admin.TabularInline):
    'Django admin tabular inline with grappelli collapsible classes added'
    classes = ('grp-collapse grp-open',)


class CatalogueInline(CollapsibleTabularInline):
    model = Catalogue
    fields = ('institution', 'call_number', 'start_year', 'end_year',
              'is_current', 'is_sammelband', 'bound_order', 'notes')


class SubjectInline(CollapsibleTabularInline):
    model = BookSubject
    fields = ('subject', 'is_primary', 'notes')


class LanguageInline(CollapsibleTabularInline):
    model = BookLanguage
    fields = ('language', 'is_primary', 'notes')

class CreatorInlineForm(forms.ModelForm):
    '''Custom model form for Book editing, used to add autocomplete
    for place lookup.'''
    class Meta:
        model = Creator
        fields = ('creator_type', 'person', 'notes')
        widgets = {
            'person': autocomplete.ModelSelect2(
                url='people:autocomplete',
                attrs={'data-placeholder': 'Start typing a name to search...'}
            )
        }

class CreatorInline(CollapsibleTabularInline):
    model = Creator
    form = CreatorInlineForm

class PersonBookInlineForm(forms.ModelForm):
    '''Custom model form for Book editing, used to add autocomplete
    for place lookup.'''
    class Meta:
        model = PersonBook
        fields = ('person', 'relationship_type', 'start_year', 'end_year',
                  'notes')
        widgets = {
            'person': autocomplete.ModelSelect2(
                url='people:autocomplete',
                attrs={'data-placeholder': 'Start typing a name to search...'}
            )
        }


class PersonBookInline(CollapsibleTabularInline):
    model = PersonBook
    form = PersonBookInlineForm


class BookAdminForm(forms.ModelForm):
    '''Custom model form for Book editing, used to add autocomplete
    for place lookup.'''
    class Meta:
        model = Book
        exclude = []
        widgets = {
            'pub_place': autocomplete.ModelSelect2(
                url='places:autocomplete',
                attrs={'data-placeholder': 'Start typing location to search...'}),
           'publisher': autocomplete.ModelSelect2(
                url='books:publisher-autocomplete',
                attrs={'data-placeholder': 'Start typing publisher name to search...'}),
           'digital_edition': ManifestSelectWidget

        }


class BookAdmin(admin.ModelAdmin):
    form = BookAdminForm

    list_display = ('short_title', 'author_names', 'pub_year',
        'catalogue_call_numbers', 'is_extant', 'is_annotated',
        'is_digitized', 'has_notes')
    # NOTE: fields are specified here so that notes input will be displayed last
    fields = ('title', 'short_title', 'original_pub_info', 'publisher',
        'pub_place', 'pub_year', 'is_extant', 'is_annotated',
        'red_catalog_number', 'ink_catalog_number', 'pencil_catalog_number',
        'dimensions', 'digital_edition', 'notes')
    search_fields = ('title', 'creator__person__authorized_name',
        'catalogue__call_number', 'notes', 'publisher__name')
    inlines = [CreatorInline, LanguageInline, SubjectInline, CatalogueInline,
        PersonBookInline, FootnoteInline]
    list_filter = ('subjects', 'languages', 'is_extant',
        'is_annotated')


class PersonBookAdmin(admin.ModelAdmin):
    # NOTE: person-book is editable on the book page, but exposing as a
    # top level as well to make it easier to associate footnotes with
    # person-book relationships
    list_display = ('person', 'relationship_type', 'book', 'start_year',
                    'end_year', 'has_notes')
    fields = ('person', 'relationship_type', 'book', 'start_year',
              'end_year', 'notes')
    inlines = [FootnoteInline]


admin.site.register(Subject,  NamedNotableBookCount)
admin.site.register(Language, NamedNotableBookCount)
admin.site.register(Publisher, NamedNotableBookCount)
admin.site.register(OwningInstitution, OwningInstitutionAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(CreatorType, NamedNotableAdmin)
admin.site.register(PersonBookRelationshipType, NamedNotableAdmin)
admin.site.register(PersonBook, PersonBookAdmin)
