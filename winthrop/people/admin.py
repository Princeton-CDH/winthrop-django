from django.contrib import admin

from .models import Person, Residence, RelationshipType, Relationship


class ResidenceInline(admin.TabularInline):
    '''Inline class for Residence'''
    model = Residence


class PersonAdmin(admin.ModelAdmin):
    inlines = [
        ResidenceInline
    ]


admin.site.register(Person, PersonAdmin)
admin.site.register(RelationshipType)
admin.site.register(Relationship)
