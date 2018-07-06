import logging

from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from djiffy.models import Manifest
from unidecode import unidecode

from winthrop.common.models import Named, Notable, DateRange
from winthrop.common.solr import Indexable
from winthrop.places.models import Place
from winthrop.people.models import Person
from winthrop.footnotes.models import Footnote


logger = logging.getLogger(__name__)


class BookCount(models.Model):
    '''Mix-in for models related to books; adds book count property and link to
    associated books'''
    class Meta:
        abstract = True

    def book_count(self):
        '''Generate a count of associated books with an admin link to
        find those books on the change list'''
        base_url = reverse('admin:books_book_changelist')
        return mark_safe('<a href="%s?%ss__id__exact=%s">%s</a>' % (
            base_url,
            self.__class__.__name__.lower(),
            self.pk,
            self.book_set.count()
        ))
    book_count.short_description = '# books'


class Subject(Named, Notable, BookCount):
    '''Subject categorization for books'''
    pass


class Language(Named, Notable, BookCount):
    '''Language that a book is written in or a language included in a book'''
    pass


class Publisher(Named, Notable, BookCount):
    '''Publisher of a book'''
    pass


class OwningInstitution(Named, Notable, BookCount):
    '''Institution that owns the extant copy of a book'''
    short_name = models.CharField(
        max_length=255, blank=True,
        help_text='Optional short name for admin display')
    contact_info = models.TextField()
    place = models.ForeignKey(Place)

    def __str__(self):
        return self.short_name or self.name


class Book(Notable, Indexable):
    '''An individual book or volume'''
    title = models.TextField()
    short_title = models.CharField(max_length=255)
    # do we want any limit on short titles?
    original_pub_info = models.TextField(
        verbose_name='Original Publication Information')
    publisher = models.ForeignKey(Publisher, blank=True, null=True)
    pub_place = models.ForeignKey(Place, verbose_name='Place of Publication',
                                  blank=True, null=True)
    pub_year = models.PositiveIntegerField(
        'Publication Year', blank=True, null=True)
    #: identifying slug for use in URLs
    slug = models.SlugField(
        max_length=255, unique=True, blank=True,
        help_text=('Readable ID for use in URLs. Automatically generated from '
                   'author, title, and year on save. Edit with *caution* '
                   'because this will break permanent links.')
    )

    # is positive integer enough, or do we need more validation here?
    is_extant = models.BooleanField(default=False)
    is_annotated = models.BooleanField(default=False)
    red_catalog_number = models.CharField(max_length=255, blank=True)
    ink_catalog_number = models.CharField(max_length=255, blank=True)
    pencil_catalog_number = models.CharField(max_length=255, blank=True)
    dimensions = models.CharField(max_length=255, blank=True)
    # expected length? is char sufficient or do we need text?

    subjects = models.ManyToManyField(Subject, through='BookSubject')
    languages = models.ManyToManyField(Language, through='BookLanguage')
    contributors = models.ManyToManyField(Person, through='Creator')

    # books are connected to owning institutions via the Catalogue
    # model; mapping as a many-to-many with a through
    # model in case we want to access owning instutions directly
    owning_institutions = models.ManyToManyField(
        OwningInstitution, through='Catalogue')

    digital_edition = models.ForeignKey(
        Manifest, blank=True, null=True,
        help_text='Digitized edition of this book, if available')

    # proof-of-concept generic relation to footnotes
    # (actual models that need this still TBD)
    footnotes = GenericRelation(Footnote)

    class Meta:
        ordering = ['title']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_slug()
        super(Book, self).save(*args, **kwargs)

    def __str__(self):
        return '%s (%s)' % (self.short_title, self.pub_year)

    def is_digitized(self):
        '''is there an associated digital edition?'''
        return self.digital_edition != None
    is_digitized.boolean = True

    def catalogue_call_numbers(self):
        '''Convenience access to catalogue call numbers, for display in admin'''
        return ', '.join([c.call_number for c in self.catalogue_set.all()])
    catalogue_call_numbers.short_description = 'Call Numbers'

    def authors(self):
        '''Contributor queryset filtered by creator type Author'''
        return self.contributor_by_type('Author')

    def author_names(self):
        '''Display author names; convenience access for display in admin'''
        # NOTE: possibly might want to use last names here
        return ', '.join(str(auth) for auth in self.authors())
    author_names.short_description = 'Authors'
    author_names.admin_order_field = 'creator__person__authorized_name'

    def add_author(self, person):
        '''Add the specified person as an author of this book'''
        self.add_creator(person, 'Author')

    def add_editor(self, person):
        '''Add the specified person as an editor of this book'''
        self.add_creator(person, 'Editor')

    def add_translator(self, person):
        '''Add the specified person as an translator of this book'''
        self.add_creator(person, 'Translator')

    def add_creator(self, person, creator_type):
        '''Associate the specified person as a creator of this book
        using the specified type (e.g., author, editor, etc.).
        Will throw an exception if creator type is not valid.'''
        creator_type = CreatorType.objects.get(name=creator_type)
        Creator.objects.create(person=person, creator_type=creator_type,
                               book=self)

    def contributor_by_type(self, creator_type):
        '''Contributors by type, e.g. author or editor. Returns an empty
        :class:`~winthrop.people.models.Person` queryset if the object is not
        yet saved.'''

        # object must be saved in order to query related items
        if self.pk:
            # order by when the creator record pk (i.e. creation order);
            # (otherwise defaults to alpha by authorized name)
            return self.contributors.filter(creator__creator_type__name=creator_type) \
                       .order_by('creator__pk')
        # return empty queryset if unsaved
        return Person.objects.none()

    def translators(self):
        '''Contributor queryset filtered by creator type Translator'''
        return self.contributor_by_type('Translator')

    def editors(self):
        '''Contributor queryset filtered by creator type Editor'''
        return self.contributor_by_type('Editor')

    def generate_slug(self):
        '''Generate a slug based on first author, title, and year.

        :rtype str: String in the format ``lastname-title-of-work-year``
        '''
        # get the first author, if there is one
        author = self.authors().first()
        if author:
            # use the last name of the first author
            author = author.authorized_name.split(',')[0]
        else:
            # otherwise, set it to an empty string
            author = ''
        # truncate the title to first several words of the title
        title = ' '.join(self.short_title.split()[:5])
        # use copyright year if available, with fallback to work year if
        year = self.pub_year or ''
        # # return a slug
        return slugify(' '.join([unidecode(author), unidecode(title), str(year)]))

    def get_absolute_url(self):
        '''URL so view this object on the public website'''
        return reverse('books:detail', kwargs={'slug': self.slug})

    def handle_person_save(sender, instance, **kwargs):
        '''signal handler for person save; reindex to get current author name'''
        if instance.authorized_name_changed:
            # only index if authorized name has changed
            logger.debug('person save, reindexing %d book(s)', instance.book_set.count())
            Indexable.index_items(instance.book_set.all(), params={'commitWithin': 3000})

    def handle_person_delete(sender, instance, **kwargs):
        '''signal handler for person delete; reindex books'''

        # get a list of ids for collected works before clearing them
        book_ids = instance.book_set.values_list('id', flat=True)

        logger.debug('peson delete, reindexing %d book(s)', len(book_ids))
        # find the items based on the list of ids to reindex
        books = Book.objects.filter(id__in=list(book_ids))

        # NOTE: this sends pre/post clear signal, but it's not obvious
        # how to take advantage of that
        instance.book_set.clear()
        Indexable.index_items(books, params={'commitWithin': 3000})

    def handle_creator_change(sender, instance, **kwargs):
        '''signal handler for creator save or delete; reindex to get any creator changes'''
        # same behavior for save or delete
        logger.debug('creator change, reindexing %s', instance.book)
        instance.book.index(params={'commitWithin': 3000})

    #: index dependencies, to update when related items are changed
    index_depends_on = {
        # author name
        'contributors': {
            'post_save': handle_person_save,
            'pre_delete': handle_person_delete,
        },
        'creator_set': {
            'post_save': handle_creator_change,
            'post_delete': handle_creator_change,
        }
    }

    def index_id(self):
        '''identifier within solr'''
        return 'book:{}'.format(self.pk)

    @property
    def thumbnail(self):
        '''IIIF image id for associated digital edition thumbnail,
        if there is one'''
        if self.digital_edition and self.digital_edition.thumbnail:
            return self.digital_edition.thumbnail.iiif_image_id

    @property
    def thumbnail_label(self):
        '''Label for the thumbnail of the associated digital edition,
        if there is one'''
        if self.digital_edition and self.digital_edition.thumbnail:
            return self.digital_edition.thumbnail.label

    @classmethod
    def content_type(cls):
        # content type as a string, for use in solr indexing
        return str(cls._meta)

    def index_data(self):
        '''data for indexing in Solr'''

        return {
            # use content type in format of app.model_name for type
            # (serializing model options as string returns this format)
            'content_type': Book.content_type(),
            'id': self.index_id(),
            'slug': self.slug,
            'title': self.title,
            'short_title': self.short_title,
            'authors': [str(author) for author in self.authors()],
            # first author only, for sorting
            # FIXME: sort on last name first? not an ordered relationship currently
            'author_exact': str(self.authors().first()) if self.authors().exists() else None,
            'pub_year': self.pub_year,
            # NOTE: this indicates whether the book is annotated, does not
            # necessarily mean there are annotations documented in our system
            'is_annotated': self.is_annotated,
            'thumbnail': self.thumbnail,
            'thumbnail_label': self.thumbnail_label
        }


class Catalogue(Notable, DateRange):
    '''Location of a book in the real world, associating it with an
    owning instutition and also handling books that are bound together.'''
    institution = models.ForeignKey(OwningInstitution)
    book = models.ForeignKey(Book)
    is_current = models.BooleanField()
    # using char instead of int because assuming  call numbers may contain
    # strings as well as numbers
    call_number = models.CharField(max_length=255, blank=True)
    is_sammelband = models.BooleanField(default=False)
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


    class Meta:
        unique_together = ('subject', 'book')


    def __str__(self):
        return '%s %s%s' % (self.book, self.subject,
            ' (primary)' if self.is_primary else '')

class BookLanguage(Notable):
    '''Through-model for book-language relationship, to allow designating
    one language as primary or adding notes.'''
    language = models.ForeignKey(Language)
    book = models.ForeignKey(Book)
    is_primary = models.BooleanField()

    class Meta:
        unique_together = ('book', 'language')

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
    person = models.ForeignKey(
        Person,
        help_text=('This association also determines if a person is added to '
                   'the annotator autocomplete.')
    )
    book = models.ForeignKey(Book)
    relationship_type = models.ForeignKey(PersonBookRelationshipType)

    class Meta:
        verbose_name = 'Person/Book Interaction'

    def __str__(self):
        dates = ''
        if self.dates:
            dates = ' (%s)' % self.dates
        return '%s: %s of %s%s' % (self.person, self.relationship_type, self.book, dates)
