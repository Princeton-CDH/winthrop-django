from django import forms
from django.contrib import admin
from django.conf import settings
from .models import Person, Residence, RelationshipType, Relationship
from dal import autocomplete

class RelationshipInline(admin.TabularInline):
    '''Inline class for Relationships'''
    model = Relationship
    fk_name = 'from_person'
    # Setting a logical order for the relationship fields
    fields = ('to_person', 'relationship_type', 'start_year',
        'end_year', 'notes')


class ResidenceInline(admin.TabularInline):
    '''Inline class for Residence'''
    model = Residence
    # Setting a logical order for the residence fields
    fields = ('place', 'start_year', 'end_year', 'notes')


class PersonAdminForm(forms.ModelForm):
    '''Custom model form for Person editing, used to add VIAF lookup'''
    class Meta:
        model = Person
        exclude = []
        widgets = {
                'authorized_name': autocomplete.Select2(
                    url='people:viaf-autosuggest',
                    attrs={
                        'data-placeholder': 'Type a name to search VIAF',
                        'data-minimum-input-length': 3
                    }
                )
        }


class PersonAdmin(admin.ModelAdmin):
    form = PersonAdminForm
    inlines = [
        ResidenceInline, RelationshipInline
    ]
    list_display = ('authorized_name', 'sort_name', 'birth', 'death',
        'viaf_id', 'family_group')
    list_filter = ('family_group',)
    fields = ('authorized_name', 'sort_name', 'viaf_id', ('birth', 'death'),
        'family_group', 'notes')
    search_fields = ('authorized_name',)

    class Media:
        static_url = getattr(settings, 'STATIC_URL')
        js = ['admin/viaf-suggest.js']


admin.site.register(Person, PersonAdmin)
admin.site.register(RelationshipType)
