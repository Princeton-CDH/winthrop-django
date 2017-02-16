from django import forms
from django.contrib import admin
from dal import autocomplete
from annotator_store.admin import AnnotationAdmin

from .models import Annotation


class AnnotationAdminForm(forms.ModelForm):
    '''Custom model form for Annotation editing; used to configure
    autocomplete lookups.'''
    class Meta:
        model = Annotation
        exclude = []
        widgets = {
            'author': autocomplete.ModelSelect2(
                url='people:autocomplete',
                attrs={'data-placeholder': 'Start typing name to search...'}),
            'canvas': autocomplete.ModelSelect2(
                url='books:canvas-autocomplete',
                attrs={'data-placeholder': 'Start typing canvas name or uri to search...'}),

        }


class WinthropAnnotationAdmin(AnnotationAdmin):
    form = AnnotationAdminForm
    list_display = ('text_preview', 'author', 'canvas', 'created',
        'updated', 'uri_link')


admin.site.unregister(Annotation)
admin.site.register(Annotation, WinthropAnnotationAdmin)