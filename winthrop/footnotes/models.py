from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class SourceType(models.Model):
    name = models.CharField(max_length=255)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Bibliography(models.Model):  # would citation be a better singular?
    bibliographic_note = models.TextField(
        help_text='Full bibliographic citation')
    source_type = models.ForeignKey(SourceType)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Bibliographies'

    def __str__(self):
        return self.bibliographic_note

class Footnote(models.Model):
    bibliography = models.ForeignKey(Bibliography)
    # location ?
    snippet_text = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    is_agree = models.BooleanField()

    # is there a meaningful short display for a footnote
    # to use for __str__ ?

    # NOTE: for convenient access from other models, add a
    # reverse generic relation
    #
    # from django.contrib.contenttypes.fields import GenericRelation
    # from winthrop.footnotes.models import Footnote
    #
    # footnotes = GenericRelation(Footnote)

