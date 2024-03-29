'''
**solr_schema** is a custom manage command to update the schema for the
configured Solr instance.  Reports on the number of fields that are
added or updated, and any that are out of date and were removed.

Actual logic implemented in
:meth:`ppa.archive.solr.SolrSchema.update_solr_schema`

Example usage::

    python manage.py solr_schema

'''

from django.core.management.base import BaseCommand, CommandError
from SolrClient.exceptions import ConnectionError

from winthrop.common import solr


class Command(BaseCommand):
    '''Add fields to schema for configured Solr instance'''
    help = __doc__

    def handle(self, *args, **kwargs):
        schema = solr.SolrSchema()
        try:
            created, updated, removed = schema.update_solr_schema()
        except ConnectionError:
            raise CommandError('Error connecting to Solr. ' +
                'Check your configuration and make sure Solr is running.')
        # summarize what was done
        if created:
            self.stdout.write('Added %d field%s' %
                (created, '' if created == 1 else 's'))
        if updated:
            self.stdout.write('Updated %d field%s' %
                (updated, '' if updated == 1 else 's'))
        if removed:
            self.stdout.write('Removed %d field%s' %
                (removed, '' if removed == 1 else 's'))

        # use solr core admin to trigger reload, so schema
        # changes take effect
        solr.CoreAdmin().reload()
