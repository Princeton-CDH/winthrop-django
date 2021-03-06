from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe
from dal import autocomplete
from djiffy.models import Canvas
from annotator_store.admin import AnnotationAdmin

from .models import Annotation, Tag
from winthrop.footnotes.admin import FootnoteInline


class CollapsibleTabularInline(admin.TabularInline):
    'Django admin tabular inline with grappelli collapsible classes added'
    classes = ('grp-collapse grp-open',)


class CanvasLinkWidget(autocomplete.ModelSelect2):
    '''Customize autocomplete select widget to include a link
    to view the related canvas on the website, since the 'view on site'
    link for an annotation resolves to the JSON API url.'''

    class Media:
        css = {
            'all': ('css/local-admin.css',)
        }

    def render(self, name, value, attrs=None):
        widget = super(CanvasLinkWidget, self).render(name, value, attrs)
        # if no canvas id is set, return widget as is
        if not value:
            return widget

        # otherwise, add a link to view the canvas on the site;
        # borrowing grappelli style for main "view on site" button
        canvas = Canvas.objects.get(id=value)
        return mark_safe(u'''%s
            <ul class="canvas-link grp-object-tools">
                <li><a href="%s" target="_blank" class="grp-state-focus">View canvas on site</a>
            </li></ul>''' % (widget, canvas.get_absolute_url()))


class AnnotationAdminForm(forms.ModelForm):
    '''Custom model form for Annotation editing; used to configure
    autocomplete lookups.'''
    class Meta:
        model = Annotation
        exclude = []
        labels = {
            # the quoted text in standard annotator.js parlance is the anchor
            # text for our annotation/marginalia
            'tags': 'Annotation type',
            'quote': 'Anchor text',
            'author': 'Annotator',
        }
        widgets = {
            'author': autocomplete.ModelSelect2(
                url='people:autocomplete',
                attrs={'data-placeholder': 'Start typing name to search...'}),
            'canvas': CanvasLinkWidget(
                url='books:canvas-autocomplete',
                attrs={'data-placeholder': 'Start typing canvas name or uri to search...'}),

        }
        fields = ('canvas', 'text', 'tags', 'text_translation', 'languages',
                  'subjects', 'author', 'quote', 'anchor_translation',
                  'anchor_languages', 'notes', 'user', 'extra_data', 'uri')


class WinthropAnnotationAdmin(AnnotationAdmin):
    # Override author field in list fiew to annotator
    # and associate its sort with author.authorized_name
    def annotator(self, obj):
        return obj.author
    annotator.short_description = 'Annotator'
    annotator.admin_order_field = 'author__authorized_name'

    form = AnnotationAdminForm
    list_display = ('admin_thumbnail', 'text_preview', 'annotator', 'canvas')
    # NOTE: 'quote' == anchor text, and should be editable
    readonly_fields = ('uri', 'extra_data')
    inlines = (FootnoteInline, )


admin.site.unregister(Annotation)
admin.site.register(Annotation, WinthropAnnotationAdmin)
admin.site.register(Tag)
