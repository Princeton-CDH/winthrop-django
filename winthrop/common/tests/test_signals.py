from unittest.mock import Mock, patch
from weakref import ref

from django.conf import settings
from django.db import models
from django.test import TestCase, override_settings
import pytest

from winthrop.books.models import Book, Creator, CreatorType
from winthrop.people.models import Person
from winthrop.common.signals import IndexableSignalHandler


def setUpModule():
    # connect indexing signal handlers for this test module only
    IndexableSignalHandler.connect()

def tearDownModule():
    # disconnect indexing signal handlers
    IndexableSignalHandler.disconnect()


@override_settings(SOLR_CONNECTIONS={'default': settings.SOLR_CONNECTIONS['test']})
class TestIndexableSignalHandler(TestCase):

    def test_connect(self):
        # check that signal handlers are connected as expected
        # - model save and delete
        post_save_handlers = [item[1] for item in models.signals.post_save.receivers]
        assert ref(IndexableSignalHandler.handle_save) in post_save_handlers
        post_del_handlers = [item[1] for item in models.signals.post_delete.receivers]
        assert ref(IndexableSignalHandler.handle_delete) in post_del_handlers
        # many to many
        m2m_handlers = [item[1] for item in models.signals.m2m_changed.receivers]
        assert ref(IndexableSignalHandler.handle_relation_change) in m2m_handlers

        # check Wintrhop specific handlers, some reused definitions from
        # above

        # - pre delete
        pre_del_handlers = [item[1] for item in models.signals.pre_delete.receivers]
        assert ref(Book.handle_related_delete) in pre_del_handlers

        # - post save
        assert ref(Book.handle_person_save) in post_save_handlers
        assert ref(Book.handle_named_save) in post_save_handlers
        assert ref(Book.handle_related_change) in post_save_handlers

        # - post delete
        assert ref(Book.handle_related_change) in post_del_handlers

    @pytest.mark.django_db
    def test_handle_save(self):
        with patch.object(Book, 'index') as mockindex:
            Book.objects.create()
            mockindex.assert_called_with(params=IndexableSignalHandler.index_params)

        # non-indexable object should be ignored
        nonindexable = Mock()
        IndexableSignalHandler.handle_save(Mock(), nonindexable)
        nonindexable.index.assert_not_called()

    @pytest.mark.django_db
    def test_handle_delete(self):
        with patch.object(Book, 'index'):
            with patch.object(Book, 'remove_from_index') as mock_rmindex:
                digwork = Book.objects.create()
                digwork.delete()
                mock_rmindex.assert_called_with(params=IndexableSignalHandler.index_params)

        # non-indexable object should be ignored
        nonindexable = Mock()
        IndexableSignalHandler.handle_delete(Mock(), nonindexable)
        nonindexable.remove_from_index.assert_not_called()

    @pytest.mark.django_db
    def test_handle_relation_change(self):
        with patch.object(Book, 'index') as mockindex:
            book = Book.objects.create(short_title='A long and arduous title', pub_year=1842)
            author1 = Person.objects.create(authorized_name='Anne Onomous')
            author = CreatorType.objects.get(name='Author')

            # NOTE: explicit through model doesn't actually trigger
            # m2m signals, so add/remove aren't actually testing the relation
            # change signal handler here

            # add author
            mockindex.reset_mock()
            Creator.objects.create(book=book, person=author1, creator_type=author)
            mockindex.assert_called_with(params=IndexableSignalHandler.index_params)

            # remove author
            mockindex.reset_mock()
            book.creator_set.filter(person=author1).delete()
            mockindex.assert_called_with(params=IndexableSignalHandler.index_params)

            # clear
            mockindex.reset_mock()
            book.contributors.clear()
            mockindex.assert_called_with(params=IndexableSignalHandler.index_params)

            # if action is not one we care about, should be ignored
            mockindex.reset_mock()
            IndexableSignalHandler.handle_relation_change(Mock(), book, 'pre_remove')
            mockindex.assert_not_called()

        # non-indexable object should be ignored
        nonindexable = Mock()
        IndexableSignalHandler.handle_relation_change(Mock(), nonindexable, 'post_add')
        nonindexable.index.assert_not_called()
