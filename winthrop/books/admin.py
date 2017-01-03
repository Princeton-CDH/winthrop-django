from django.contrib import admin

from winthrop.common.admin import NamedNotableAdmin
from .models import Subject, Language, Publisher, OwningInstitution, \
    Book, Catalogue, BookSubject, BookLanguage, CreatorType, Creator, \
    PersonBook, PersonBookRelationshipType

class OwningInstitutionAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'name', 'place', 'has_notes')
    fields = ('name', 'short_name', 'contact_info', 'place', 'notes')
    search_fields = ('name', 'short_name', 'contact_info', 'notes')


class SubjectInline(admin.TabularInline):
    model = BookSubject


class BookAdmin(admin.ModelAdmin):
    list_display = ('short_title', 'publisher', 'pub_year', 'is_annotated',
        'is_digitized', 'is_extant')
    # TODO: order edit fields so notes displays last
    inlines = [SubjectInline]
    list_filter = ('subjects', 'languages')


admin.site.register(Subject,  NamedNotableAdmin)
admin.site.register(Language, NamedNotableAdmin)
admin.site.register(Publisher, NamedNotableAdmin)
admin.site.register(OwningInstitution, OwningInstitutionAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Catalogue)
admin.site.register(CreatorType)
# NOTE: these will probably be inlines, but register for testing for now
admin.site.register(BookSubject)
admin.site.register(BookLanguage)
admin.site.register(Creator)
admin.site.register(PersonBook)
admin.site.register(PersonBookRelationshipType)
