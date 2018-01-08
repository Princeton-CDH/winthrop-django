import re

from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from winthrop.common.models import Named, Notable, DateRange
from winthrop.footnotes.models import Footnote
from winthrop.places.models import Place
from winthrop.people.viaf import ViafEntity


class AliasIntegerField(models.IntegerField):
    '''Alias field adapted from https://djangosnippets.org/snippets/10440/
    to allow accessing an existing db field by a different name, both
    for user display and in model and queryset use.
    '''

    def contribute_to_class(self, cls, name, virtual_only=False):
        super(AliasIntegerField, self).contribute_to_class(cls, name, virtual_only=True)
        setattr(cls, name, self)

    def __get__(self, instance, instance_type=None):
        return getattr(instance, self.db_column)

    def __set__(self, instance, value, instance_type=None):
        return setattr(instance, self.db_column, value)


class Person(Notable, DateRange):
    '''Person'''
    authorized_name = models.CharField(max_length=255)
    viaf_id = models.URLField(null=True, blank=True)
    # alias start/end year from DateRange to be more readable and semantic
    birth = AliasIntegerField(db_column='start_year', null=True, blank=True)
    death = AliasIntegerField(db_column='end_year', null=True, blank=True)
    sort_name = models.CharField(max_length=255, blank=True)
    family_group = models.CharField(max_length=255, blank=True)
    footnotes = GenericRelation(Footnote)
    relationships = models.ManyToManyField('self', through='Relationship',
        related_name='related_to', symmetrical=False)
    # NOTE: django doesn't allow many-to-many to self with a through
    # table to be symmetrical

    class Meta:
        verbose_name_plural = 'People'
        ordering = ['authorized_name']

    def save(self, *args, **kwargs):
        '''Adds birth and death dates if they aren't already set
        and there's a viaf id for the record'''

        if self.viaf_id and not self.birth and not self.death:
            self.set_birth_death_years()

        super(Person, self).save(*args, **kwargs)

    def __str__(self):
        return self.authorized_name

    @property
    def viaf(self):
        if self.viaf_id:
            return ViafEntity(self.viaf_id)

    def set_birth_death_years(self):
        '''Set local birth and death dates based on information from VIAF'''
        if self.viaf_id:
            self.birth = self.viaf.birthyear
            self.death = self.viaf.deathyear


class Residence(Notable, DateRange):
    '''A residence where a person lived at some point in time'''
    person = models.ForeignKey(Person)
    place = models.ForeignKey(Place)

    def __str__(self):
        dates = ''
        if self.dates:
            dates = ' (%s)' % self.dates
        return '%s %s%s' % (self.person, self.place, dates)


class RelationshipType(Named, Notable):
    '''Types of relationships between people'''
    is_symmetric = models.BooleanField(default=False)

class Relationship(Notable, DateRange):
    '''A specific relationship between two people.'''
    from_person = models.ForeignKey(Person, related_name='from_relationships')
    to_person = models.ForeignKey(Person, related_name='to_relationships')
    relationship_type = models.ForeignKey(RelationshipType)

    def __str__(self):
        return '%s %s %s' % (self.from_person, self.relationship_type,
            self.to_person)
