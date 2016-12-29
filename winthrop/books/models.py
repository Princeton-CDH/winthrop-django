from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from winthrop.common.models import Named, Notable, DateRange
from winthrop.places.models import Place
from winthrop.people.models import Person
from winthrop.footnotes.models import Footnote


class Subject(Named, Notable):
    '''Subject categorization for books'''
    pass

class Language(Named, Notable):
    '''Language that a book is written in or a language included in a book'''
    pass

class Publisher(Named, Notable):
    '''Publisher of a book'''
    pass

class OwningInstitution(Named, Notable):
    '''Institution that owns the extant copy of a book'''
    short_name = models.CharField(max_length=255, blank=True,
        help_text='Optional short name for admin display')
    contact_info = models.TextField()
    place = models.ForeignKey(Place)

    def __str__(self):
        return self.short_name or self.name


class Book(Notable):
    '''An individual book or volume'''
    title = models.CharField(max_length=255)
    # how long are full titles? is this long enough?
    short_title = models.CharField(max_length=255)
    # do we want any limit on short titles?
    original_pub_info = models.TextField()
    publisher = models.ForeignKey(Publisher)
    pub_place = models.ForeignKey(Place)
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

    subjects = models.ManyToManyField(Subject, through='BookSubject')
    languages = models.ManyToManyField(Language, through='BookLanguage')

    # books are connected to owning institutions via the Catalogue
    # model; mapping as a many-to-many with a through
    # model in case we want to access owning instutions directly
    owning_institutions = models.ManyToManyField(OwningInstitution,
        through='Catalogue')

    # proof-of-concept generic relation to footnotes
    # (actual models that need this still TBD)
    footnotes = GenericRelation(Footnote)

    def __str__(self):
        return '%s (%s)' % (self.short_title, self.pub_year)


class Catalogue(Notable, DateRange):
    '''Location of a book in the real world, associating it with an
    owning instutition and also handling books that are bound together.'''
    institution = models.ForeignKey(OwningInstitution)
    book = models.ForeignKey(Book)
    is_current = models.BooleanField()
    # using char instead of int because assuming "number" is not strictly required
    call_number = models.CharField(max_length=255, blank=True)
    is_sammelband = models.BooleanField()
    bound_order = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        dates = ''
        if self.dates:
            dates = ' (%s)' % self.dates
        return '%s / %s%s' % (self.book, self.institution, dates)


class BookSubject(Notable):
    '''Through-model for book-subject relationship, to allow designating
    a particular subject as primary or adding notes.'''
    subject = models.ForeignKey(Subject)
    book = models.ForeignKey(Book)
    is_primary = models.BooleanField()

    def __str__(self):
        return '%s %s%s' % (self.book, self.subject,
            ' (primary)' if self.is_primary else '')


class BookLanguage(Notable):
    '''Through-model for book-language relationship, to allow designating
    one language as primary or adding notes.'''
    language = models.ForeignKey(Language)
    book = models.ForeignKey(Book)
    is_primary = models.BooleanField()

    def __str__(self):
        return '%s %s%s' % (self.book, self.language,
            ' (primary)' if self.is_primary else '')


class CreatorType(Named, Notable):
    '''Type of creator role a person can have to a book - author,
    editor, translator, etc.'''
    pass


class Creator(Notable):
    creator_type = models.ForeignKey(CreatorType)
    person = models.ForeignKey(Person)
    book = models.ForeignKey(Book)

    def __str__(self):
        return '%s %s %s' % (self.person, self.creator_type, self.book)

class PersonBookRelationshipType(Named, Notable):
    '''Type of non-annotation relationship assocating a person
    with a book.'''
    pass


class PersonBook(Notable, DateRange):
    '''Interactions or connections between books and people other than
    annotation.'''
    # FIXME: better name? concept/thing/model
    person = models.ForeignKey(Person)
    book = models.ForeignKey(Book)
    relationship_type = models.ForeignKey(PersonBookRelationshipType)

    def __str__(self):
        dates = ''
        if self.dates:
            dates = ' (%s)' % self.dates
        return '%s - %s%s' % (self.person, self.book, dates)
