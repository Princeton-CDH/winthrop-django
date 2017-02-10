from django.db import models
from annotator_store.models import BaseAnnotation
from djiffy.models import IfPage
from winthrop.people.models import Person


# NOTE: needs to be different name than Annotation due to reverse rel issues...
class Annotation(BaseAnnotation):
    # NOTE: do we want to associate explicitly with canvas in the db?
    # could just use uri, but faster lookup if we associate...
    canvas = models.ForeignKey(IfPage, null=True, blank=True)
    author = models.ForeignKey(Person, null=True, blank=True)


    def info(self):
        print('local info!!!')
        info = super(Annotation, self).info()
        info['extra_data'] = 'foo'
        return info




