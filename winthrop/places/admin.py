from django.contrib import admin

from .models import Place

class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'geonames_id', 'has_notes')
    fields = ('name', 'geonames_id', 'notes')
    search_fields = ('name', 'notes', 'geonames_id')

admin.site.register(Place, PlaceAdmin)
