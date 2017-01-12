import csv
from django.core.management.base import BaseCommand, CommandError

from winthrop.books.models import Book, Publisher, OwningInstitution, \
    Catalogue
from winthrop.people.models import Person
from winthrop.places.models import Place

# questions:
# - am I correct to assume all books in the spreadsheet are extant?
# - are there any cases with multiple authors, editors, or translators?
# - in some cases 'annotated' column has notes; preserve these somewhere?
# - I don't see any subjects in the spreadsheet, is that correct?
# - which field or fields should be used for physical description?


class Command(BaseCommand):
    help = 'Import NYSL book data into the database from a CSV file'

    #: mapping of book model fields that can be filled in exactly as is
    #: from corresponding columns in the spreadsheet data
    fields_exact = {
        'title': 'Title',
        'short_title': 'Short Title',
        'pub_year': 'Year of Publication',
        'red_catalog_number': 'RED catalogue number at the front',
        'ink_catalog_number': 'INK catalogue number at the front',
        'pencil_catalog_number': 'PENCIL catalogue number at the front',
        'original_pub_info': 'PUB INFO - Original',
        'notes': 'Notes'
    }

    #: fields that require cleanup, related model lookup, or other logic
    fields = {
        'pub_year': 'Year of Publication',
        'is_annotated': 'Annotated?',
        'pub_place': 'Modern Place of Publication',
        'publisher': 'Standardized Name of Publisher',
        # NYSL cataloguing information
        'nysl_call_number': 'NYSL CALL NUMBER',
        'nysl_notes': 'NYSL -- NOTES'
    }

    # creator type and corresponding column in the spreadsheet
    creators = {
        'Author': 'AUTHOR, Standarized',
        'Translator': 'Translator',
        'Editor': 'Editor',
    }

    other_fields = [
        'Number of Pages',
        'NYSL -- NOTES',
        'NYSL CALL NUMBER',
        'Type of Volume',
        'Subject Tagging (separate with semicolons)',
        'EDITION',
        'Books with important relationships to this text (separate with semicolons)',
        'NYSL DESCRIPTION',
        'Other documents that demonstrate this relationship (separate with semicolon)',
        'Provenance',
        'Annotated?',
        'Physical Size'
    ]

    def add_arguments(self, parser):
        parser.add_argument('input_file')

    def handle(self, *args, **kwargs):
        input_file = kwargs['input_file']

        # TODO: create fixture for NYSL & NYC ?

        # all books will be catalogued with NYSL, so look for
        # owning instution object first
        try:
            nysl = OwningInstitution.objects.get(short_name='NYSL')
        except OwningInstitution.DoesNotExist:
            raise CommandError("Owning institution NYSL was not found")

        # TODO: add stats, report on number of books, people,
        # publishers, places added

        with open(input_file) as csvfile:
            csvreader = csv.DictReader(csvfile)

            count = 0
            # each row in the CSV corresponds to a book record
            for row in csvreader:
                # nysl books, therefore assuming all are extant
                newbook = Book(is_extant=True)
                # set fields that can be mapped directly from the spreadsheet
                for model_field, csv_field in self.fields_exact.items():
                    value = row[csv_field]
                    # special case: some of the catalog numbers have
                    # been entered as "NA" in the spreadsheet; skip those
                    print('field %s value %s' % (model_field, value))
                    if model_field.endswith('catalog_number') and \
                        value == 'NA':
                        continue

                    setattr(newbook, model_field, value)

                # handle book fields that require some logic
                # - publication year might have brackets, e.g. [1566],
                #   but model stores it as an integer
                pub_year = row[self.fields['pub_year']]
                newbook.pub_year = pub_year.strip('[]')
                # - is annotated; spreadsheet has variants in upper/lower case
                # and trailing periods; in some cases there are notes;
                # for now, assuming that anything ambiguous should be false here
                annotated = row[self.fields['is_annotated']].lower().strip('.')
                newbook.is_annotated = (annotated == 'yes')

                # add required relationships before saving the new book
                # - place
                placename = row[self.fields['pub_place']]
                try:
                    place = Place.objects.get(name=placename)
                except Place.DoesNotExist:
                    place = Place.objects.create(name=placename)
                newbook.pub_place = place

                # - publisher
                publisher_name = row[self.fields['publisher']]
                try:
                    publisher = Publisher.objects.get(name=publisher_name)
                except Publisher.DoesNotExist:
                    publisher = Publisher.objects.create(name=publisher_name)
                newbook.publisher = publisher

                newbook.save()

                # TODO: do we need to handle multiple creators here?
                for creator_type, csv_field in self.creators.items():
                    # name could be empty (e.g. for translator, editor)
                    name = row[csv_field]
                    if name:
                        try:
                            person = Person.objects.get(authorized_name=name)
                        except Person.DoesNotExist:
                            person = Person.objects.create(authorized_name=name)
                        newbook.add_creator(person, creator_type)

                # catalogue as a current NYSL book
                Catalogue.objects.create(institution=nysl, book=newbook,
                    is_current=True,
                    call_number=row[self.fields['nysl_call_number']],
                    notes=row[self.fields['nysl_notes']])

                count += 1
                # bail out for testing
                if count > 3:
                    return

