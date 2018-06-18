from io import StringIO
from unittest.mock import patch, Mock

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
import pytest

from winthrop.books.models import Book
from winthrop.common.management.commands import index
from winthrop.common.solr import get_solr_connection


class TestSolrSchemaCommand(TestCase):

    def test_connection_error(self):
        # simulate no solr running
        with override_settings(SOLR_CONNECTIONS={'default':
                              {'COLLECTION': 'bogus',
                               'URL': 'http://localhost:191918984/solr/'}}):
            with pytest.raises(CommandError):
                call_command('solr_schema')

    @pytest.mark.usefixtures("empty_solr")
    def test_empty_solr(self):
        stdout = StringIO()
        call_command('solr_schema', stdout=stdout)
        output = stdout.getvalue()
        assert 'Added ' in output
        assert 'Updated ' not in output

    @pytest.mark.usefixtures("solr")
    def test_update_solr(self):
        stdout = StringIO()
        call_command('solr_schema', stdout=stdout)
        output = stdout.getvalue()
        assert 'Updated ' in output
        assert 'Added ' not in output

        # create field to be removed
        solr, coll = get_solr_connection()
        solr.schema.create_field(
            coll, {'name': 'bogus', 'type': 'string', 'required': False})
        call_command('solr_schema', stdout=stdout)
        output = stdout.getvalue()
        assert 'Removed 1 field' in output


class TestIndexCommand(TestCase):
    fixtures = ['sample_book_data']

    @patch('winthrop.common.management.commands.index.Indexable')
    def test_index(self, mockindexable):
        # index data into solr and catch  an error
        cmd = index.Command()
        cmd.solr = Mock()
        cmd.solr_collection = 'test'

        test_index_data = range(5)
        cmd.index(test_index_data)
        mockindexable.index_items.assert_called_with(test_index_data, progbar=None)

        # solr connection exception should raise a command error
        with pytest.raises(CommandError):
            mockindexable.index_items.side_effect = Exception
            cmd.index(test_index_data)

    @patch('winthrop.common.management.commands.index.get_solr_connection')
    @patch('winthrop.common.management.commands.index.progressbar')
    @patch.object(index.Command, 'index')
    def test_call_command(self, mock_cmd_index_method, mockprogbar, mock_get_solr):
        mocksolr = Mock()
        test_coll = 'test'
        mock_get_solr.return_value = (mocksolr, test_coll)
        books = Book.objects.all()

        stdout = StringIO()
        call_command('index', stdout=stdout)
        print(stdout.getvalue())

        # index all books
        # (can't use assert_called_with because querysets doesn't evaluate equal)
        # mock_cmd_index_method.assert_called_with(books)
        args = mock_cmd_index_method.call_args[0]
        # first arg is queryset; compare them as lists
        assert list(books) == list(args[0])

        # not enough data to run progress bar
        mockprogbar.ProgressBar.assert_not_called()
        # commit called after works are indexed
        mocksolr.commit.assert_called_with(test_coll)
        # only called once (no pages)
        assert mock_cmd_index_method.call_count == 1
