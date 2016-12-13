from django.db import models

from winthrop.common.models import Named, Notable, DateRange
from winthrop.places.models import Place

# Create your models here.
 # - people, residences, relationships, relationship types
 # - people_books (how people relate to books they didn't write)

class Person(Notable):
    authorized_name = models.CharField(max_length=255)
    # do we want to store bare id or URI here?
    viaf_id = models.PositiveIntegerField(null=True, blank=True)
    sort_name = models.CharField(max_length=255, blank=True)
    family_group = models.CharField(max_length=255, blank=True)
    relationships = models.ManyToManyField('self', through='Relationship',
        related_name='related_to', symmetrical=False)
    # NOTE: django doesn't allow many-to-many to self with a through
    # table to be symmetrical

    class Meta:
        verbose_name_plural = 'People'

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
    pass


class Relationship(Notable, DateRange):
    '''A specific relationship between two people.'''
    from_person = models.ForeignKey(Person, related_name='from_people')
    to_person = models.ForeignKey(Person, related_name='to_people')
    relationship_type = models.ForeignKey(RelationshipType)

    def __str__(self):
        return '%s %s %s' % (self.from_person, self.relationship_type,
            self.to_person)
