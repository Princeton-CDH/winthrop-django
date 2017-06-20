'''
Import command for Winthrop team's spreadsheet. It can be invoked using::

    python manage.py import_nysql [--justsammel] /path/to/csv

The ``--justsammel`` flag skips import of records to avoid
reproducing duplicates, but rebuilds the ``is_sammelband`` flag set and
produces an output list.

The expect behavior is designed for a once-off import and will produce
duplicate book entries (but not duplicates of any entries created
as part of book creation).

All persons created attempt to have a VIAF uri associated and all places
have a Geonames ID assigned if possible.
'''

from collections import defaultdict
from itertools import chain
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
    '''Import NYSL book data into the database from a CSV file'''
    help = __doc__

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
        'flagged_info': 'FLAGGED PAGES FOR REPRODUCTION',
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
        parser.add_argument(
            '--justsammel',
            action='store_true',
            dest='just_sammel',
            default=False,
            help='Just make sammelband connections'
        )

    def handle(self, *args, **kwargs):
        input_file = kwargs['input_file']
        self.mocking = False
        # TODO: create fixture for NYSL & NYC ?

        # all books will be catalogued with NYSL, so look for
        # owning instution object first
        # (no need to check because NYSL is preloaded by migrations)
        self.nysl = OwningInstitution.objects.get(short_name='NYSL')

        self.stats = defaultdict(int)
        if not kwargs['just_sammel']:
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

        # Now look for is_sammelband and set the flag
        self.build_sammelband()

    def viaf_lookup(self, name):
        viaf = ViafAPI()
        viafid = None
        results = viaf.suggest(name)
        # Handle no results
        if results:
            # Check for a 'nametype' and make sure it's personal
            if 'nametype' in results[0]:
                if results[0]['nametype'] == 'personal':
                    viafid = viaf.uri_from_id(results[0]['viafid'])
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
        # aside from removing periods
        for model_field, csv_field in self.fields_exact.items():
            value = data[csv_field]
            # special case: some of the catalog numbers have
            # been entered as "NA" in the spreadsheet; skip those
            if model_field.endswith('catalog_number') and \
                value == 'NA':
                continue
            # special case: some books are missing a short title
            # supply those with first three words of title
            if model_field == 'short_title' and not value:
                words = data['Title'].strip('. ').split()
                value = (' '.join(words[0:3])).strip('.')
            # special case: strip periods for title and short_title
            if model_field == 'title':
                value = data['Title'].strip('. ')

            setattr(newbook, model_field, value)

        # handle book fields that require some logic
        # - publication year might have brackets, e.g. [1566],
        #   but model stores it as an integer
        stripped_spaces_only = data[self.fields['pub_year']].strip()
        pub_year = data[self.fields['pub_year']].strip('[]?.nd ')
        if re.search('-|i\.e\.', pub_year):
            if newbook.notes:
                newbook.notes += '\n\nAdditional Publication Year Info: %s' %\
                    stripped_spaces_only
            else:
                newbook.notes = 'Additional Publication Year Info: %s' %\
                    stripped_spaces_only
            pub_year = (re.match(r'\d+?(?=\D)', pub_year)).group(0)

        if pub_year:
            newbook.pub_year = pub_year
        # - is annotated; spreadsheet has variants in upper/lower case
        # and trailing periods; in some cases there are notes;
        # for now, assuming that anything ambiguous should be false here
        annotated = data[self.fields['is_annotated']].lower().strip('. ')
        newbook.is_annotated = (annotated == 'yes')

        # - flagged_info; pull info for flagged pages and add if it exists
        if annotated == 'yes':
            flagged_info = data[self.fields['flagged_info']].strip()
            if flagged_info:
                if newbook.notes:
                    newbook.notes += '\n\nReproduction Recommendation: %s' %\
                        flagged_info
                else:
                    newbook.notes = 'Reproduction Recommendation: %s' %\
                        flagged_info

        # add required relationships before saving the new book
        # - place
        placename = data[self.fields['pub_place']].strip(' ?[]()')
        if placename and len((re.sub(r'[.,]', '', placename))) < 3:
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
        publisher_name = data[self.fields['publisher']].strip("?. ")
        # Catch np/sn
        if publisher_name and len(publisher_name) < 4:
            publisher_name = None
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
            name = name.strip('?. []')
            # Get various versions of 'Not sure' and remove name if they exist
            if re.search(r'[Vv]arious|[A|a]nonymous|[N|n]one [G|g]iven', name):
                name = None
            # Use four characters as a dumb filter to toss stray 'np'/'sn'
            if name and len(name) <= 4:
                name = None
            if name:
                try:
                    person = Person.objects.get(authorized_name=name)
                except Person.DoesNotExist:
                    viafid = self.viaf_lookup(name)
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

    def build_sammelband(self):
        '''Create sammelband flag for books with same/similar NYSL catalog numbers'''
        # All the catalogues just created
        catalogue_set = Catalogue.objects.all()
        # Call number list, not yet made unique
        call_nos = []
        self.stdout.write('Now checking for bound volumes:')
        for catalogue in catalogue_set:
                # Remove letters that obscure sammelbands
                call_search = (catalogue.call_number).strip('abcdefgh')
                match_count = 0
                for entry in catalogue_set:
                    search_re = re.compile(r'%s$' % call_search)
                    if re.match(search_re,
                                (entry.call_number).strip('abcdefgh')):
                        match_count += 1
                # If match happened more than once, assume sammelband
                if match_count > 1:
                    call_nos.append(catalogue.call_number)
                    catalogue.is_sammelband = True
                    catalogue.save()
        # A sorted unique vol list
        sorted_vols = sorted(list(set(call_nos)))
        # Get a list of books that are associated with a sammelband entry
        cat_list = []
        for number in sorted_vols:
            q = Catalogue.objects.filter(call_number=number)
            cat_list = chain(cat_list, q)

        self.stdout.write('    Number of call numbers that seem to have '
                          'multiple bound titles: %s' % len(sorted_vols))
        self.stdout.write('The following titles are marked as sammelband:')
        # Good old fashioned for-loop with iterator to build a list for the team
        i = 1
        for cat in cat_list:
            self.stdout.write('    %s. Short Title: %s - NYSL Call Number: %s'
                              % (i, cat.book.short_title, cat.call_number))
            i += 1
