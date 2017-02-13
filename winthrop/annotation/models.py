from urllib.parse import urlparse
from django.db import models
from django.urls import resolve, Resolver404
from annotator_store.models import BaseAnnotation
from djiffy.models import IfPage
from winthrop.people.models import Person


class Annotation(BaseAnnotation):
    # NOTE: do we want to associate explicitly with canvas in the db?
    # could just use uri, but faster lookup if we associate...
    canvas = models.ForeignKey(IfPage, null=True, blank=True)
    author = models.ForeignKey(Person, null=True, blank=True)


    def info(self):
        info = super(Annotation, self).info()
        info['extra_data'] = 'foo'
        return info

    def save(self, *args, **kwargs):
        # NOTE: could probably set the canvas uri in javascript instead
        # of using page uri, but for now determine canvas id
        # based on the page uri
        try:
            match = resolve(urlparse(self.uri).path)
            if match.url_name == 'page' and 'djiffy' in match.namespaces:
                self.canvas = IfPage.objects.get(
                    short_id=match.kwargs['id'],
                    book__short_id=match.kwargs['book_id']
                )
        except Resolver404:
            pass

        super(Annotation, self).save()




