from django.contrib import admin

from .models import SourceType, Bibliography, Footnote

class FootnoteAdmin(admin.ModelAdmin):
    related_lookup_fields = {
        'generic': [['content_type', 'object_id']]
    }


admin.site.register(SourceType)
admin.site.register(Bibliography)
admin.site.register(Footnote, FootnoteAdmin)