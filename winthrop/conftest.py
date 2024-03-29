from django.conf import settings
from django.test import override_settings
import pytest

from winthrop.common.solr import SolrSchema, CoreAdmin, get_solr_connection


@pytest.fixture
def empty_solr():
    # pytest solr fixture; updates solr schema
    with override_settings(SOLR_CONNECTIONS={'default': settings.SOLR_CONNECTIONS['test']}):
        # reload core before and after to ensure field list is accurate
        CoreAdmin().reload()
        solr_schema = SolrSchema()
        cp_fields = solr_schema.solr.schema.get_schema_copyfields(solr_schema.solr_collection)
        current_fields = solr_schema.solr_schema_fields()

        for cp_field in cp_fields:
            solr_schema.solr.schema.delete_copy_field(solr_schema.solr_collection, cp_field)
        for field in current_fields:
            # don't delete default/built-in fields!
            if field == 'id' or field.startswith('_'):
                continue
            solr_schema.solr.schema.delete_field(solr_schema.solr_collection, field)
        CoreAdmin().reload()

        # yield settings so tests run with overridden solr connection
        yield settings


@pytest.fixture
def solr():
    # pytest solr fixture; updates solr schema
    with override_settings(SOLR_CONNECTIONS={'default': settings.SOLR_CONNECTIONS['test']}):
        # reload core before and after to ensure field list is accurate
        solr_schema = SolrSchema()
        CoreAdmin().reload()
        solr_schema.update_solr_schema()
        CoreAdmin().reload()


        # yield settings so tests run with overridden solr connection
        yield settings

        # clear out any data indexed in test collection
        solr_schema.solr.delete_doc_by_query(solr_schema.solr_collection, '*:*')
