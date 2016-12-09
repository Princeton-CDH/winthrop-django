from django.db import models

from winthrop.places.models import Place

# Create your models here.
 # - people, residences, relationships, relationship types
 # - people_books (how people relate to books they didn't write)

class Person(models.Model):
    authorized_name = models.CharField(max_length=255)
    # do we want to store bare id or URI here?
    viaf_id = models.PositiveIntegerField(null=True, blank=True)
    sort_name = models.CharField(max_length=255, blank=True)
    family_group = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    relationships = models.ManyToManyField('self', through='Relationship',
        related_name='related_to', symmetrical=False)
    # NOTE: django doesn't allow many-to-many to self with a through
    # table to be symmetrical

    class Meta:
        verbose_name_plural = 'People'

    def __str__(self):
        return self.authorized_name


class Residence(models.Model):
    person = models.ForeignKey(Person)
    place = models.ForeignKey(Place)
    start_year = models.PositiveIntegerField(null=True, blank=True)
    end_year = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)

    @property
    def dates(self):
        # FIXME: not quite right; display start- or -end if only one is present
        # or just year if they are the same
        # (also in books; make re-usable?)
        return '-'.join([str(year) for year in [self.start_year, self.end_year] if year])

    def __str__(self):
        dates = ''
        if self.dates:
            dates = ' (%s)' % self.dates
        return '%s  %s%s' % (self.person, self.place, dates)


class RelationshipType(models.Model):
    '''Types of relationships between people'''
    name = models.CharField(max_length=255)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Relationship(models.Model):
    '''A specific relationship between two people.'''
    from_person = models.ForeignKey(Person, related_name='from_people')
    to_person = models.ForeignKey(Person, related_name='to_people')
    relationship_type = models.ForeignKey(RelationshipType)
    start_year = models.PositiveIntegerField(null=True, blank=True)
    end_year = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return '%s %s %s' % (self.from_person, self.relationship_type,
            self.to_person)
