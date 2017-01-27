from django.db import models

from winthrop.common.models import Named, Notable, DateRange
from winthrop.places.models import Place

# alias field adapted from https://djangosnippets.org/snippets/10440/
class AliasField(models.Field):
    def contribute_to_class(self, cls, name, virtual_only=False):
        super(AliasField, self).contribute_to_class(cls, name, virtual_only=True)
        setattr(cls, name, self)

    def __get__(self, instance, instance_type=None):
        return getattr(instance, self.db_column)

    def __set__(self, instance, value, instance_type=None):
        return setattr(instance, self.db_column, value)


class Order(models.Model):
    """
    The main order model
    """
    number = AliasField(db_column='id')

class Person(Notable, DateRange):
    authorized_name = models.CharField(max_length=255)
    viaf_id = models.URLField(null=True, blank=True)
    # alias start/end year from DateRange to be more readable and semantic
    birth = AliasField(db_column='start_year', null=True, blank=True)
    death = AliasField(db_column='end_year', null=True, blank=True)
    sort_name = models.CharField(max_length=255, blank=True)
    family_group = models.CharField(max_length=255, blank=True)
    relationships = models.ManyToManyField('self', through='Relationship',
        related_name='related_to', symmetrical=False)
    # NOTE: django doesn't allow many-to-many to self with a through
    # table to be symmetrical

    class Meta:
        verbose_name_plural = 'People'
        ordering = ['authorized_name']

    def __str__(self):
        return self.authorized_name


class Residence(Notable, DateRange):
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
    from_person = models.ForeignKey(Person, related_name='from_people')
    to_person = models.ForeignKey(Person, related_name='to_people')
    relationship_type = models.ForeignKey(RelationshipType)

    def __str__(self):
        return '%s %s %s' % (self.from_person, self.relationship_type,
            self.to_person)
