from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from winthrop.common.models import Named, Notable


class SourceType(Named, Notable):
    '''Type of source document.'''
    pass


class Bibliography(Notable):  # would citation be a better singular?
    bibliographic_note = models.TextField(
        help_text='Full bibliographic citation')
    source_type = models.ForeignKey(SourceType)

    class Meta:
        verbose_name_plural = 'Bibliographies'

    def __str__(self):
        return self.bibliographic_note


class Footnote(Notable):
    '''Footnote that can be associated with any other model via
    generic relationship.  Used to provide supporting documentation
    for or against information in the system.
    '''
    bibliography = models.ForeignKey(Bibliography)
    location = models.TextField(blank=True,
        help_text='Page number for a book, URL for part of a website,' +
        ' or other location inside of a larger work.')
    snippet_text = models.TextField(blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    is_agree = models.BooleanField(help_text='True if the evidence ' +
        'supports the information in the system, False if it contradicts.')

    def __str__(self):
        'Footnote on %s' % (self.content_object)

    # NOTE: for convenient access from other models, add a
    # reverse generic relation
    #
    # from django.contrib.contenttypes.fields import GenericRelation
    # from winthrop.footnotes.models import Footnote
    #
    # footnotes = GenericRelation(Footnote)

