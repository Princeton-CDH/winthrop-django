
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.http.request import HttpRequest
from django.utils.safestring import mark_safe
from annotator_store.models import BaseAnnotation
from djiffy.models import Canvas
from winthrop.common.models import Named, Notable
from winthrop.people.models import Person
from winthrop.books.models import Subject, Language


class AnnotationCount(models.Model):
    '''Mix-in for models related to annotations; adds annotation count property
    and link to associated annotations'''
    class Meta:
        abstract = True

    def annotation_count(self):
        base_url = reverse('admin:annotations_annotation_changelist')
        return mark_safe('<a href="%s?%ss__id__exact=%s">%s</a>' % (
                            base_url,
                            self.__class__.__name__.lower(),
                            self.pk,
                            self.annotation_set.count()
                ))
    annotation_count.short_description = '# annotations'


class Tag(Named, Notable):
    '''Stub model for tag'''
    pass


class Annotation(BaseAnnotation):
    # NOTE: do we want to associate explicitly with canvas in the db?
    # could just use uri, but faster lookup if we associate...
    canvas = models.ForeignKey(Canvas, null=True, blank=True)
    author = models.ForeignKey(Person, null=True, blank=True)

    # Annotations are connected to subjects in roughly the same way as Books
    subjects = models.ManyToManyField(Subject, through='AnnotationSubject')

    # Annotations and tags about their characteristics associated with Tags
    tags = models.ManyToManyField(Tag, through='AnnotationTag')

    # Annotations are connected to Languages like books, with flags for annotation
    # language and anchor text language
    languages = models.ManyToManyField(Language, through='AnnotationLanguage')

    def save(self, *args, **kwargs):
        # for image annotation, URI should be set to canvas URI; look up
        # canvas by URI and associate with the record

        # if canvas is already set and uri matches annotation uri, do nothing
        if self.canvas and self.uri == self.canvas.uri:
            pass
        else:
            # otherwise, lookup canvas and associate
            # (clear out in case there is no match for the new uri)
            self.canvas = None
            try:
                self.canvas = Canvas.objects.get(uri=self.uri)
            except Canvas.DoesNotExist:
                pass
        super(Annotation, self).save()

        # Handle updating the object so that any fields from handle_extra_data
        # populate correctly

        # Dummmy http request that we won't be using but handle extra data
        # expects
        request = HttpRequest()
        self.handle_extra_data(self.extra_data, request)

    def handle_extra_data(self, data, request):
        '''Handle any "extra" data that is not part of the stock annotation
        data model.  Use this method to customize the logic for updating
        an annotation from json request data (as sent by annotator.js).'''

        if 'author' in data and 'id' in data['author']:
            self.author = Person.objects.get(id=data['author']['id'])
            del data['author']
        else:
            # clear out in case previously set
            self.author = None
        if 'tags' in data:
            # First, clear out any tags and re-create them --in case user
            # deletes in annotator
            related_tags = AnnotationTag.objects.filter(annotation=self)
            related_tags.delete()
            for tag in data['tags']:
                # Enforcing tag vocabulary, so we want to pass
                # if it isn't there. Otherwise create the tag.
                try:
                    tag = tag.strip(', ')
                    tag_obj = Tag.objects.get(name=tag)
                    annotation_tag, c = AnnotationTag.objects.get_or_create(
                        annotation=self,
                        tag=tag_obj
                    )
                except ObjectDoesNotExist:
                    pass
            del data['tags']

            if 'anchortext' in data:
                self.quote = data['anchortext']
                del data['anchortext']
            else:
                self.quote = None

            if 'language' in data:
                related_languages = AnnotationLanguage.objects.filter(
                    annotation=self,
                    is_annotation_lang=True)
                related_languages.delete()
                for language in data['language']:
                    try:
                        lang = Language.objects.get(name=language)
                        lang_note, c = AnnotationLanguage.objects.get_or_create(
                            annotation=self,
                            language=lang,
                            is_annotation_lang=True,
                        )
                    except ObjectDoesNotExist:
                        pass
                del data['language']

            if 'anchorLanguage' in data:
                related_languages = AnnotationLanguage.objects.filter(
                    annotation=self,
                    is_anchor_lang=True)
                related_languages.delete()
                try:
                    for language in data['anchorLanguage']:
                        lang = Language.objects.get(name=language)
                        lang_note, c = AnnotationLanguage.objects.get_or_create(
                            annotation=self,
                            language=lang,
                            is_anchor_lang=True,
                        )
                except ObjectDoesNotExist:
                    pass
                del data['anchorLanguage']
        return data

    def info(self):
        # extend the default info impleentation (used to generate json)
        # to include local database fields in the output
        info = super(Annotation, self).info()
        if self.author:
            info['author'] = {
                'name': self.author.authorized_name,
                'id': self.author.id,
            }
        related_tags = AnnotationTag.objects.filter(annotation=self)
        related_langs = AnnotationLanguage.objects.filter(
            annotation=self,
            is_annotation_lang=True,
        )
        related_anchor_langs = AnnotationLanguage.objects.filter(
            annotation=self,
            is_anchor_lang=True,
        )
        info['tags'] = [
            related_tag.tag.name
            for related_tag in related_tags
        ]
        if self.quote:
            info['anchortext'] = self.quote
        info['language'] = [
            related_lang.language.name
            for related_lang in related_langs
        ]
        info['anchorLanguage'] = [
            related_lang.language.name
            for related_lang in related_anchor_langs
        ]
        return info

    img_info_to_iiif = {'w': 'width', 'h': 'height', 'x': 'x', 'y': 'y'}

    def iiif_image_selection(self):
        # if image selection information is present in annotation
        # and canvas is associated, generated a IIIF image for the
        # selected portion of the canvas
        if 'image_selection' in self.extra_data and self.canvas:
            # convert stored image info into the format used by
            # piffle for generating iiif image region
            img_selection = {
                self.img_info_to_iiif[key]: float(val.rstrip('%'))
                for key, val in self.extra_data['image_selection'].items()
                if key in self.img_info_to_iiif
            }
            return self.canvas.image.region(percent=True, **img_selection)

    def admin_thumbnail(self):
        img_selection = self.iiif_image_selection()
        # if image selection is available, display small thumbnail
        if img_selection:
            return u'<img src="%s" />' % img_selection.mini_thumbnail()
        # otherwise, if canvas is set, display canvas small thumbnail
        elif self.canvas:
            return u'<img src="%s" />' % self.canvas.image.mini_thumbnail()
    admin_thumbnail.short_description = 'Thumbnail'
    admin_thumbnail.allow_tags = True


class AnnotationSubject(Notable, AnnotationCount):
    '''Through model for subjects and their linked annotations'''
    subject = models.ForeignKey(Subject)
    annotation = models.ForeignKey(Annotation)
    is_primary = models.BooleanField()

    class Meta:
        unique_together = ('annotation', 'subject')

    def __str__(self):
        return '%s %s%s' % (self.annotation, self.subject,
            ' (primary)' if self.is_primary else '')


class AnnotationTag(Notable, AnnotationCount):
    '''Through model for associating tags and annotations'''
    tag = models.ForeignKey(Tag)
    annotation = models.ForeignKey(Annotation)

    class Meta:
        unique_together = ('tag', 'annotation')

    def __str__(self):
        return '%s %s' % (self.annotation, self.tag)


class AnnotationLanguage(Notable, AnnotationCount):
    '''Through model for associating tags and annotations'''
    annotation = models.ForeignKey(Annotation)
    language = models.ForeignKey(Language)
    is_annotation_lang = models.BooleanField(default=False)
    is_anchor_lang = models.BooleanField(default=False)

    class Meta:
        unique_together = ('language', 'annotation', 'is_annotation_lang',
            'is_anchor_lang')

    def __str__(self):
        return '%s %s' % (self.annotation, self.language)
