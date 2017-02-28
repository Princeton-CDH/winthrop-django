from collections import defaultdict
import csv
import re
from django.core.management.base import BaseCommand, CommandError

from winthrop.books.models import Book, Publisher, OwningInstitution, \
    Catalogue
from winthrop.people.models import Person
from winthrop.people.viaf import ViafAPI
from winthrop.places.models import Place
from winthrop.places.geonames import GeoNamesAPI


class Command(BaseCommand):
    help = 'Import NYSL book data into the database from a CSV file'

    #: mapping of book model fields that can be filled in exactly as is
    #: from corresponding columns in the spreadsheet data
    fields_exact = {
        'title': 'Title',
        'short_title': 'Short Title',
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

    # currently unused
    other_fields = [
        'Number of Pages',
        'Type of Volume',
        'Subject Tagging (separate with semicolons)',
        'EDITION',
        'Books with important relationships to this text (separate with semicolons)',
        'NYSL DESCRIPTION',
        'Other documents that demonstrate this relationship (separate with semicolon)',
        'Provenance',
        'Physical Size'
    ]

    def add_arguments(self, parser):
        parser.add_argument('input_file')

    def handle(self, *args, **kwargs):
        input_file = kwargs['input_file']
        self.mocking = False
        # TODO: create fixture for NYSL & NYC ?

        # all books will be catalogued with NYSL, so look for
        # owning instution object first
        try:
            self.nysl = OwningInstitution.objects.get(short_name='NYSL')
        except OwningInstitution.DoesNotExist:
            raise CommandError("Owning institution NYSL was not found")

        self.stats = defaultdict(int)

        with open(input_file) as csvfile:
            csvreader = csv.DictReader(csvfile)

            # each row in the CSV corresponds to a book record
            for row in csvreader:
                try:
                    self.create_book(row)
                except Exception as err:
                    print('Error on import for %s: %s' %
                        (row['Short Title'][:30], err))
                    self.stats['err'] += 1

            # summarize what content was imported/created
            self.stdout.write('''Imported content:
    %(book)d books
    %(place)d places
    %(person)d people
    %(publisher)d publishers

%(err)d errors''' % self.stats)

    def viaf_lookup(self, name):
        viaf = ViafAPI()
        viafid = None
        results = viaf.suggest(name)
        # Handle no results
        if results != []:
            # Check for a 'nametype' and make sure it's personal
            if 'nametype' in results[0]:
                if results[0]['nametype'] == 'personal':
                    viafid = results[0]['viafid']
        return viafid

    def geonames_lookup(self, place_name):
        '''Function to wrap a GeoNames lookup and assign info.
        Returns a dict for Place generator or None'''
        geo = GeoNamesAPI()
        # Get the top hit and presume the API guessed correctly
        result = geo.search(place_name, max_rows=1)
        place_dict = {}
        if result:
            place_dict['latitude'] = float(result[0]['lat'])
            place_dict['longitude'] = float(result[0]['lng'])
            place_dict['geonames_id'] = geo.uri_from_id(result[0]['geonameId'])
            return place_dict
        else:
            return None

    def create_book(self, data):
        # create a new book and all related models from
        # a row of data in the spreadsheet

        # nysl books, therefore assuming all are extant
        newbook = Book(is_extant=True)
        # set fields that can be mapped directly from the spreadsheet
        for model_field, csv_field in self.fields_exact.items():
            value = data[csv_field]
            # special case: some of the catalog numbers have
            # been entered as "NA" in the spreadsheet; skip those
            if model_field.endswith('catalog_number') and \
                value == 'NA':
                continue

            setattr(newbook, model_field, value)

        # handle book fields that require some logic
        # - publication year might have brackets, e.g. [1566],
        #   but model stores it as an integer
        pub_year = data[self.fields['pub_year']].strip('[]?. ')
        if pub_year:
            newbook.pub_year = pub_year
        # - is annotated; spreadsheet has variants in upper/lower case
        # and trailing periods; in some cases there are notes;
        # for now, assuming that anything ambiguous should be false here
        annotated = data[self.fields['is_annotated']].lower().strip('.')
        newbook.is_annotated = (annotated == 'yes')

        # add required relationships before saving the new book
        # - place
        placename = data[self.fields['pub_place']].strip(' ?[]()')
        # Dumb filter for sn/np
        if len((re.sub(r'[.,]', '', placename))) < 3:
            placename = None
        if placename:
            try:
                place = Place.objects.get(name=placename)
            except Place.DoesNotExist:
                place_dict = self.geonames_lookup(placename)
                if place_dict:
                    place = Place.objects.create(name=placename, **place_dict)
                else:
                    place = Place.objects.create(
                        name=placename,
                        latitude=0.0,
                        longitude=0.0,
                    )
                self.stats['place'] += 1
            newbook.pub_place = place

        # - publisher
        publisher_name = data[self.fields['publisher']].strip("? ")
        if publisher_name:
            try:
                publisher = Publisher.objects.get(name=publisher_name)
            except Publisher.DoesNotExist:
                publisher = Publisher.objects.create(name=publisher_name)

            self.stats['publisher'] += 1
            newbook.publisher = publisher

        newbook.save()

        # TODO: do we need to handle multiple creators here?
        for creator_type, csv_field in self.creators.items():
            # name could be empty (e.g. for translator, editor)
            name = data[csv_field]
            # Get rid of any last stray periods, if they exist
            name = name.strip('?. ')
            # Use four characters as a dumb filter to toss stray 'np'/'sn'
            if len(name) <= 4:
                name = None
            if name:
                try:
                    person = Person.objects.get(authorized_name=name)
                except Person.DoesNotExist:
                    viafid = self.viaf_lookup(name)
                    if viafid:
                        viafid = ViafAPI.uri_from_id(viafid)
                    person = Person.objects.create(authorized_name=name,
                                viaf_id=viafid)
                    self.stats['person'] += 1
                newbook.add_creator(person, creator_type)

        # catalogue as a current NYSL book
        Catalogue.objects.create(institution=self.nysl, book=newbook,
            is_current=True,
            call_number=data[self.fields['nysl_call_number']],
            notes=data[self.fields['nysl_notes']])

        self.stats['book'] += 1
