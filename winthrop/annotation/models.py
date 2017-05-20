
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

    # Winthrop specific fields
    text_translation = models.TextField(blank=True,
        verbose_name='Annotation text translation')
    anchor_translation = models.TextField(blank=True,
        verbose_name='Anchor text translation')
    # Override since we want this to be potentially optional
    quote = models.TextField(blank=True)
    # Annotations are connected to subjects in roughly the same way as Books
    subjects = models.ManyToManyField(Subject)
    # Annotations and tags about their characteristics associated with Tags
    tags = models.ManyToManyField(Tag)
    # language and anchor text language
    languages = models.ManyToManyField(Language)
    anchor_languages = models.ManyToManyField(Language, related_name='+')

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

    def handle_extra_data(self, data, request):
        '''Handle any "extra" data that is not part of the stock annotation
        data model.  Use this method to customize the logic for updating
        an annotation from json request data (as sent by annotator.js).'''


        # NOTE: Working on the presumption that any data not included in the
        # JSON Extra data should be removed if it's added to a Django database
        # field or model
        if 'author' in data and 'id' in data['author']:
            try:
                self.author = Person.objects.get(id=data['author']['id'])
            except (ObjectDoesNotExist, ValueError):
                self.author = None
            del data['author']
        else:
            # clear out in case previously set
            self.author = None
        if 'tags' in data:
            # TODO: check if commas are being passed, again handle in js
            # NOTE: tag vocabulary is enforced; unrecognized tags
            # are ignored.
            tags = Tag.objects.filter(name__in=data['tags'])
            self.tags.set(tags)
            del data['tags']

        if 'anchortext' in data:
            self.quote = data['anchortext']
            del data['anchortext']
        else:
            self.quote = ''

        if 'language' in data:
            langs = Language.objects.filter(name__in=data['language'])
            self.languages.set(langs)
            del data['language']

        if 'anchorLanguage' in data:
            anchor_langs = Language.objects.filter(
                name__in=data['anchorLanguage'])
            self.anchor_languages.set(anchor_langs)
            del data['anchorLanguage']

        if 'subject' in data:
            subjects = Subject.objects.filter(name__in=data['subject'])
            self.subjects.set(subjects)
            del data['subject']

        if 'translation' in data:
            self.text_translation = data['translation']
            del data['translation']
        else:
            self.text_translation = ''
        if 'anchorTranslation' in data:
            self.anchor_translation = data['anchorTranslation']
            del data['anchorTranslation']
        else:
            self.anchor_translation = ''

        return data

    def info(self):
        '''Passes fields that are included on the annotation model into the
        JSON object representation of the annotation'''
        # extend the default info implementation (used to generate json)
        # to include local database fields in the output
        info = super(Annotation, self).info()
        if self.author:
            info['author'] = {
                'name': self.author.authorized_name,
                'id': self.author.id,
            }

        info.update({
            'tags': [tag.name for tag in self.tags.all()],
            'language': [language.name for language in self.languages.all()],
            'anchorLanguage': [language.name for language in self.anchor_languages.all()],
            'subjects': [subject.name for subject in self.subjects.all()]
        })
        if self.text_translation:
            info['translation'] = self.text_translation
        if self.anchor_translation:
            info['anchorTranslation'] = self.anchor_translation

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


    def __str__(self):
        return '%s %s' % (self.annotation, self.language)
