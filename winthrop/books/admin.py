from django.contrib import admin

from winthrop.common.admin import NamedNotableAdmin
from .models import Subject, Language, Publisher, OwningInstitution, \
    Book, Catalogue, BookSubject, BookLanguage, CreatorType, Creator, \
    PersonBook, PersonBookRelationshipType


class NamedNotableBookCount(NamedNotableAdmin):
    list_display = NamedNotableAdmin.list_display + ('book_count', )


class OwningInstitutionAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'name', 'place', 'has_notes', 'book_count')
    fields = ('name', 'short_name', 'contact_info', 'place', 'notes')
    search_fields = ('name', 'short_name', 'contact_info', 'notes')


class CatalogueInline(admin.TabularInline):
    model = Catalogue
    fields = ('institution', 'call_number', 'start_year', 'end_year',
        'is_current', 'is_sammelband', 'bound_order', 'notes')

class SubjectInline(admin.TabularInline):
    model = BookSubject
    fields = ('subject', 'is_primary', 'notes')


class LanguageInline(admin.TabularInline):
    model = BookLanguage
    fields = ('language', 'is_primary', 'notes')


class CreatorInline(admin.TabularInline):
    model = Creator
    fields = ('creator_type', 'person', 'notes')


class BookAdmin(admin.ModelAdmin):
    list_display = ('short_title', 'author_names', 'pub_year',
        'catalogue_call_numbers', 'is_extant', 'is_annotated',
        'is_digitized')
    # NOTE: fields are specified here so that notes input will be displayed last
    fields = ('title', 'short_title', 'original_pub_info', 'publisher',
        'pub_place', 'pub_year', 'is_extant', 'is_annotated', 'is_digitized',
        'red_catalog_number', 'ink_catalog_number', 'pencil_catalog_number',
        'dimensions', 'notes')

    inlines = [CreatorInline, LanguageInline, SubjectInline, CatalogueInline]
    list_filter = ('subjects', 'languages')


admin.site.register(Subject,  NamedNotableBookCount)
admin.site.register(Language, NamedNotableBookCount)
admin.site.register(Publisher, NamedNotableBookCount)
admin.site.register(OwningInstitution, OwningInstitutionAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Catalogue)
admin.site.register(CreatorType)
# NOTE: these will probably be inlines, but register for testing for now
admin.site.register(Creator)
admin.site.register(PersonBook)
admin.site.register(PersonBookRelationshipType)
