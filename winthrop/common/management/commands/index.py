'''
**index** is a custom manage command to index winthrop content
into Solr.

By default, indexes _all_ indexable content.

A progress bar will be displayed by default if there are more than 5
items to process.  This can be suppressed via script options.

Example usage::

    # index everything
    python manage.py index
    # index specific items
    python manage.py index htid1 htid2 htid3
    # index works only (skip pages)
    python manage.py index -i works
    python manage.py index --works
    # index pages only (skip works)
    python manage.py index -i pages
    python manage.py index ---pages
    # suppress progressbar
    python manage.py index --no-progress

'''


from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum
import progressbar
# from urllib3.exceptions import HTTPError
#from SolrClient.exceptions import ConnectionError
#from requests.exceptions import RequestException

from winthrop.common.solr import get_solr_connection, Indexable

class Command(BaseCommand):
    '''Reindex digitized items into Solr that have already been imported'''
    help = __doc__

    solr = None
    solr_collection = None
    stats = None

    options = {}
    #: normal verbosity level
    v_normal = 1
    verbosity = v_normal

    #: solr params for index call; currently set to commit within 3 seconds
    solr_index_opts = {"commitWithin": 3000}

    def add_arguments(self, parser):
        # todo: generate based on Indexable subclasses?
        # parser.add_argument(
        #     '-i', '--index', choices=['all', 'works', 'pages'], default='all',
        #     help='Index only works or pages (by default indexes all)')
        # parser.add_argument(
        #     '-w', '--works', dest='index', const='works', action='store_const',
        #     help='Index works only')
        # parser.add_argument(
        #     '-p', '--pages', dest='index', const='pages', action='store_const',
        #     help='Index pages only')
        parser.add_argument(
            '--no-progress', action='store_true',
            help='Do not display progress bar to track the status of the reindex.')

    def handle(self, *args, **kwargs):
        self.solr, self.solr_collection = get_solr_connection()
        self.verbosity = kwargs.get('verbosity', self.v_normal)
        self.options = kwargs

        total_to_index = 0
        for model in Indexable.__subclasses__():
            # total works to be indexed;
            # currently assuming all indexables are django models
            total_to_index += model.objects.count()

        # initialize progressbar if requested and indexing more than 5 items
        progbar = None
        if not self.options['no_progress'] and total_to_index > 5:
            progbar = progressbar.ProgressBar(redirect_stdout=True,
                                              max_value=total_to_index)

        for model in Indexable.__subclasses__():
            # index in chunks and update progress bar
            self.index(model.objects.all(), progbar=progbar)

        if progbar:
            progbar.finish()

        self.solr.commit(self.solr_collection)

    def index(self, index_data, progbar=None):
        '''index an iterable into the configured solr instance
        and solr collection'''

        # NOTE: currently no good way to catch a connection
        # error when Solr is not running because we get multiple
        # connections during handling of exceptions.
        try:
            # index in chunks and update progress bar if there is one
            return Indexable.index_items(index_data, params=self.solr_index_opts,
                                         progbar=progbar)
        except Exception as err:
        # except (ConnectionError, RequestException) as err:
            # NOTE: this is fairly ugly, and catching the more specific errors
            # doesn't work because there are multiple exceptions
            # thrown when a connection error occurs; however, this will
            # at least stop the script instead of repeatedly throwing
            # connection errors
            raise CommandError(err)
