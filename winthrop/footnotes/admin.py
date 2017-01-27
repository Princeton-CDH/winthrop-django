from django.contrib import admin

from winthrop.common.admin import NamedNotableAdmin
from .models import SourceType, Bibliography, Footnote

class FootnoteAdmin(admin.ModelAdmin):
    related_lookup_fields = {
        'generic': [['content_type', 'object_id']]
    }


class SourceTypeAdmin(NamedNotableAdmin):
    list_display = NamedNotableAdmin.list_display + ('item_count', )


class BibliographyAdmin(admin.ModelAdmin):
    list_display = ('bibliographic_note', 'source_type', 'has_notes',
        'footnote_count')
    search_fields = ('bibliographic_note', 'notes')


admin.site.register(SourceType, SourceTypeAdmin)
admin.site.register(Bibliography, BibliographyAdmin)
admin.site.register(Footnote, FootnoteAdmin)