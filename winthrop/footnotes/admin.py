from django.contrib import admin

from .models import SourceType, Bibliography, Footnote

admin.site.register(SourceType)
admin.site.register(Bibliography)
admin.site.register(Footnote)