from django.db import models

from winthrop.places.models import Place
from winthrop.people.models import Person


class Subject(models.Model):
    '''Subject categorization for books'''
    name = models.CharField(max_length=255)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Language(models.Model):
    '''Language that a book is written in or included in a book'''
    name = models.CharField(max_length=255)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Publisher(models.Model):
    '''Publisher of a book'''
    name = models.CharField(max_length=255)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name


class OwningInstitution(models.Model):
    '''Institution that owns the extant copy of a book'''
    name = models.CharField(max_length=255)
    # added short name so we can include full name: good/bad ?
    short_name = models.CharField(max_length=255, blank=True)
    contact_info = models.TextField()
    place = models.ForeignKey(Place)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.short_name or self.name


class Book(models.Model):
    '''An individual book or volume'''
    title = models.CharField(max_length=255)
    # how long are full titles? is this long enough?
    short_title = models.CharField(max_length=255)
    # do we want any limit on short titles?
    original_pub_info = models.TextField()
    publisher = models.ForeignKey(Publisher)
    place = models.ForeignKey(Place)
    pub_year = models.PositiveIntegerField('Publication Year')
    # is positive integer enough, or do we need more validation here?
    is_extant = models.BooleanField()
    is_annotated = models.BooleanField()
    is_digitized = models.BooleanField()
    red_catalog_number = models.CharField(max_length=255, blank=True)
    ink_catalog_number = models.CharField(max_length=255, blank=True)
    pencil_catalog_number = models.CharField(max_length=255, blank=True)
    dimensions = models.CharField(max_length=255, blank=True)
    # expected length? is char sufficient or do we need text?
    notes = models.TextField(blank=True)

    subjects = models.ManyToManyField(Subject, through='BookSubject')
    languages = models.ManyToManyField(Language, through='BookLanguage')

    # books are connected to owning institutions via the Catalogue
    # model; mapping as a many-to-many with a through
    # model in case we want to access owning instutions directly
    owning_institutions = models.ManyToManyField(OwningInstitution,
        through='Catalogue')

    def __str__(self):
        return '%s (%s)' % (self.short_title, self.pub_year)


class Catalogue(models.Model):
    '''Location of a book in the real world, associating it with an
    owning instutition and also handling books that are bound together.'''
    institution = models.ForeignKey(OwningInstitution)
    book = models.ForeignKey(Book)
    start_year = models.PositiveIntegerField(null=True, blank=True)
    end_year = models.PositiveIntegerField(null=True, blank=True)
    is_current = models.BooleanField()
    # using char instead of int because assuming "number" is not strictly required
    call_number = models.CharField(max_length=255, blank=True)
    is_sammelband = models.BooleanField()
    bound_order = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)

    @property
    def dates(self):
        return '-'.join([year for year in [self.start_year, self.end_year] if year])

    def __str__(self):
        dates = ''
        if self.dates:
            dates = ' (%s)' % self.dates
        return '%s / %s%s' % (self.book, self.institution, dates)


class BookSubject(models.Model):
    '''Through-model for book-subject relationship, to allow designating
    a particular subject as primary or adding notes.'''
    subject = models.ForeignKey(Subject)
    book = models.ForeignKey(Book)
    is_primary = models.BooleanField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return '%s %s%s' % (self.book, self.subject,
            ' (primary)' if self.is_primary else '')


class BookLanguage(models.Model):
    '''Through-model for book-language relationship, to allow designating
    one language as primary or adding notes.'''
    language = models.ForeignKey(Language)
    book = models.ForeignKey(Book)
    is_primary = models.BooleanField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return '%s %s%s' % (self.book, self.language,
            ' (primary)' if self.is_primary else '')


class CreatorType(models.Model):
    '''Type of creator role a person can have to a book - author,
    editor, translator, etc.'''
    name = models.CharField(max_length=255)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Creator(models.Model):
    creator_type = models.ForeignKey(CreatorType)
    person = models.ForeignKey(Person)
    book = models.ForeignKey(Book)
    notes = models.TextField(blank=True)

    def __str__(self):
        return '%s %s %s' % (self.person, self.creator_type, self.book)


class PersonBook(models.Model):
    '''Interactions or connections between books and people other than
    annotation.'''
    # FIXME: better name? concept/thing/model
    person = models.ForeignKey(Person)
    book = models.ForeignKey(Book)
    start_year = models.PositiveIntegerField(null=True, blank=True)
    end_year = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)

    @property
    def dates(self):
        # FIXME: not quite right; display start- or -end if only one is present
        # or just year if they are the same
        # (also in books; make re-usable?)
        # DEFINITELY make re-usable as an abstract model
        return '-'.join([str(year) for year in [self.start_year, self.end_year] if year])

    def __str__(self):
        dates = ''
        if self.dates:
            dates = ' (%s)' % self.dates
        return '%s - %s%s' % (self.person, self.book, dates)