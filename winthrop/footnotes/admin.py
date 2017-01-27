from django.contrib import admin

from .models import SourceType, Bibliography, Footnote

class FootnoteAdmin(admin.ModelAdmin):
    related_lookup_fields = {
        'generic': [['content_type', 'object_id']]
    }


class SourceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'item_count', 'has_notes')


admin.site.register(SourceType, SourceTypeAdmin)
admin.site.register(Bibliography)
admin.site.register(Footnote, FootnoteAdmin)