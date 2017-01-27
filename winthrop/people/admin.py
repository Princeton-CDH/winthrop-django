from django.contrib import admin

from .models import Person, Residence, RelationshipType, Relationship


class RelationshipInline(admin.TabularInline):
    '''Inline class for Relationships'''
    model = Relationship
    fk_name = 'from_person'


class ResidenceInline(admin.TabularInline):
    '''Inline class for Residence'''
    model = Residence


class PersonAdmin(admin.ModelAdmin):
    inlines = [
        ResidenceInline, RelationshipInline
    ]
    list_display = ('authorized_name', 'sort_name', 'birth', 'death',
        'viaf_id', 'family_group')
    list_filter = ('family_group',)
    fields = ('authorized_name', 'sort_name', 'viaf_id', ('birth', 'death'),
        'family_group')



admin.site.register(Person, PersonAdmin)
admin.site.register(RelationshipType)
