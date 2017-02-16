from urllib.parse import urlparse
from django.db import models
from django.urls import resolve, Resolver404
from annotator_store.models import BaseAnnotation
from djiffy.models import Canvas
from winthrop.people.models import Person


class Annotation(BaseAnnotation):
    # NOTE: do we want to associate explicitly with canvas in the db?
    # could just use uri, but faster lookup if we associate...
    canvas = models.ForeignKey(Canvas, null=True, blank=True)
    author = models.ForeignKey(Person, null=True, blank=True)


    def info(self):
        info = super(Annotation, self).info()
        info['extra_data'] = 'foo'
        return info

    def save(self, *args, **kwargs):
        # for image annotation, URI should be set to canvas URI; look up
        # canvas by URI and associate with the record
        self.canvas = None
        try:
            self.canvas = Canvas.objects.get(uri=self.uri)
        except Canvas.DoesNotExist:
            pass

        super(Annotation, self).save()

    def handle_extra_data(self, data, request):
        '''Handle any "extra" data that is not part of the stock annotation
        data model.  Use this method to customize the logic for updating
        an annotation from request data.'''
        if 'author' in data:
            self.author = Person.objects.get(id=data['author']['id'])
            del data['author']

        return data

    def info(self):
        # extend the default info impleentation (used to generate json)
        # to include local database fields in the output
        info = super(Annotation, self).info()
        if self.author:
            info['author'] = {
                'name': self.author.authorized_name,
                'id': self.author.id
            }
        return info





