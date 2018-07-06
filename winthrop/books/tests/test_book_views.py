from datetime import datetime
import json
from time import sleep
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.template.defaultfilters import escape
from django.test import TestCase
from django.urls import reverse
import pytest
from SolrClient.exceptions import SolrError

from winthrop.books.models import Book
from winthrop.common.solr import Indexable, PagedSolrQuery
from winthrop.common.views import LastModifiedMixin


class TestBookViews(TestCase):
    fixtures = ['sample_book_data', 'test_book_details']

    def setUp(self):
        # create an admin user to test autocomplete views
        self.password = 'pass!@#$'
        self.admin = get_user_model().objects.create_superuser('testadmin',
            'test@example.com', self.password)

    def test_publisher_autocomplete(self):
        pub_autocomplete_url = reverse('books:publisher-autocomplete')
        result = self.client.get(pub_autocomplete_url,
            params={'q': 'van der'})
        # not allowed to anonymous user
        assert result.status_code == 302

        # login as an admin user
        self.client.login(username=self.admin.username, password=self.password)

        result = self.client.get(pub_autocomplete_url, {'q': 'van der'})
        assert result.status_code == 200
        # decode response to inspect
        data = json.loads(result.content.decode('utf-8'))
        assert data['results'][0]['text'] == 'E. van der Erve'

    def test_language_autocomplete(self):
        language_autocomplete_url = reverse('books:language-autocomplete')
        result = self.client.get(language_autocomplete_url,
            params={'q': 'latin'})
        # not allowed to anonymous user
        assert result.status_code == 302

        # login as an admin user
        self.client.login(username=self.admin.username, password=self.password)

        result = self.client.get(language_autocomplete_url, {'q': 'lat'})
        assert result.status_code == 200
        # decode response to inspect
        data = json.loads(result.content.decode('utf-8'))
        assert data['results'][0]['text'] == 'Latin'

    def test_subject_autocomplete(self):
        subject_autocomplete_url = reverse('books:subject-autocomplete')
        result = self.client.get(subject_autocomplete_url,
            params={'q': 'chron'})
        # not allowed to anonymous user
        assert result.status_code == 302

        # login as an admin user
        self.client.login(username=self.admin.username, password=self.password)

        result = self.client.get(subject_autocomplete_url, {'q': 'chron'})
        assert result.status_code == 200
        # decode response to inspect
        data = json.loads(result.content.decode('utf-8'))
        assert data['results'][0]['text'] == 'Chronology'

    def test_canvas_autocomplete(self):
        canvas_autocomplete_url = reverse('books:canvas-autocomplete')

        result = self.client.get(canvas_autocomplete_url,
            params={'q': '00000150'})
        # not allowed to anonymous user
        assert result.status_code == 302

        # login as an admin user
        self.client.login(username=self.admin.username, password=self.password)

        # search by partial label
        result = self.client.get(canvas_autocomplete_url, {'q': '000150'})
        assert result.status_code == 200
        data = json.loads(result.content.decode('utf-8'))
        assert data['results'][0]['id'] == '10465'
        # search by partial uri
        result = self.client.get(canvas_autocomplete_url, {'q': 'pqn59s484h'})
        data = json.loads(result.content.decode('utf-8'))
        assert data['results'][0]['id'] == '10465'

    @pytest.mark.usefixtures("solr")
    def test_book_list(self):
        url = reverse('books:list')

         # nothing indexed - should find nothing
        response = self.client.get(url)
        assert response.status_code == 200
        self.assertContains(response, 'No results')

        books = Book.objects.all()

        # index books for subsequent searches
        Indexable.index_items(books, params={'commitWithin': 500})
        sleep(2)

         # no query or filters, should find all books
        response = self.client.get(url)
        assert response.status_code == 200
        # last modified header should be set on response
        assert response.has_header('last-modified')

        # no easy way to get last modification time from Solr...
        index_modified = PagedSolrQuery({
            'q': '*:*',
            'sort': 'last_modified desc',
            'fq': 'content_type:(%s)' % str(Book._meta)
            })[0]['last_modified']
        index_modified_dt = datetime.strptime(index_modified, '%Y-%m-%dT%H:%M:%S.%fZ')

        modified = index_modified_dt.strftime('%a, %d %b %Y %H:%M:%S GMT')
        assert response['Last-Modified'] == modified


        # provisional text
        self.assertContains(response, 'Displaying %d books' % books.count())

        # NOTE: total currently not displayed
        for book in books:
            self.assertContains(response, book.short_title)
            self.assertContains(response, book.pub_year)
            for creator in book.authors():
                self.assertContains(response, creator.authorized_name)

        # annotated badge should be displayed for books marked as annotated
        annotated_count = books.filter(is_annotated=True).count()
        self.assertContains(response, '<div class="ui label">annotated</div>',
                            count=annotated_count)

        # check a book with a digital edition
        book = books.filter(digital_edition__isnull=False).first()
        canvas = book.digital_edition.thumbnail
        response = self.client.get(url)
        # should include image urls (1x/2x)
        self.assertContains(response, str(canvas.image.size(height=218)))
        self.assertContains(response, str(canvas.image.size(height=436)))
        # should include image label
        self.assertContains(response, canvas.label)

        ### keyword search
        # - one match
        response = self.client.get(url, {'query': 'mercurii'})
        self.assertContains(response, 'Displaying 1 book')
        mercurii_bk = Book.objects.get(title__contains='Mercurii')
        self.assertContains(response, mercurii_bk.short_title)
        self.assertContains(response, mercurii_bk.pub_year)

        # - no match
        response = self.client.get(url, {'query': 'astronomiae'})
        self.assertContains(response, 'No results found')
        # - bad search syntax
        response = self.client.get(url, {'query': '"astronomiae'})
        self.assertContains(response, 'Unable to parse search query')
        # last modified header should NOT be set on response
        assert not response.has_header('last-modified')

        ### sort
        # bad sort option (relevance / no keyword) ignored
        response = self.client.get(url, {'sort': 'relevance'})
        # all books displayed
        self.assertContains(response, 'Displaying %d books' % books.count())
        # ordered by author by default
        # (books without author currently listed last)
        authored_books = Book.objects.filter(creator__isnull=False) \
            .order_by('creator__person__authorized_name')
        assert response.context['object_list'][0]['short_title'] == \
            authored_books.first().short_title

        response = self.client.get(url, {'sort': 'pub_year_asc'})
        books = Book.objects.order_by('pub_year')
        assert response.context['object_list'][0]['pub_year'] == books.first().pub_year

    @pytest.mark.usefixtures("solr")
    def test_book_detail(self):
        # find an annotated book with an author
        book = Book.objects.filter(is_annotated=True, creator__creator_type__name='Author').first()

        response = self.client.get(book.get_absolute_url())
        assert response.status_code == 200
        # details that are expected to display
        self.assertContains(response, escape(book.title))
        self.assertContains(response, book.short_title)
        self.assertContains(response, book.pub_year)
        self.assertContains(response, "annotated")
        self.assertContains(response, escape(book.original_pub_info))
        self.assertContains(response, book.publisher.name)
        self.assertContains(response, book.pub_place.name)
        self.assertContains(response, book.authors().first().authorized_name)
        catalogue = book.catalogue_set.first()
        self.assertContains(response, '%s %s' % (catalogue.institution, catalogue.call_number))
        # headings that should not display because there is no data
        self.assertNotContains(response, 'Translator')
        self.assertNotContains(response, 'Editor')
        self.assertNotContains(response, 'Book Language')
        self.assertNotContains(response, 'Book Subject')
        self.assertNotContains(response, 'Person/Book interactions')
        # none should not be displayed for any missing/empty fields
        self.assertNotContains(response, "None")

        # find a book with a digital edition
        book = Book.objects.filter(digital_edition__isnull=False).first()
        canvas = book.digital_edition.thumbnail
        response = self.client.get(book.get_absolute_url())
        # should include image urls (1x/2x)
        self.assertContains(response, str(canvas.image.size(height=218)))
        self.assertContains(response, str(canvas.image.size(height=436)))
        # should include image label
        self.assertContains(response, canvas.label)

        # book without annotations
        book = Book.objects.filter(is_annotated=False).first()
        response = self.client.get(book.get_absolute_url())
        self.assertNotContains(response, "annotated")

        # last modified header not set because not available from Solr
        assert not response.has_header('last-modified')

        # index to test last-modified logic
        book.index(params={'commitWithin': 500})
        sleep(2)

         # no query or filters, should find all books
        response = self.client.get(book.get_absolute_url())
        assert response.status_code == 200
        # last modified header should be set on response
        assert response.has_header('last-modified')

        # no easy way to get last modification time from Solr...
        index_modified = PagedSolrQuery({
            'q': 'id:"%s"' % book.index_id(),
            })[0]['last_modified']
        index_modified_dt = LastModifiedMixin.solr_timestamp_to_datetime(index_modified)
        modified = index_modified_dt.strftime('%a, %d %b %Y %H:%M:%S GMT')
        assert response['Last-Modified'] == modified

        # solr error on getting last modified shouldn't break the page
        with patch('winthrop.books.views.PagedSolrQuery') as mockpagedsolrq:
            mockpagedsolrq.side_effect = SolrError
            response = self.client.get(book.get_absolute_url())
            # should return ok but with no last modified header
            assert response.status_code == 200
            assert not response.has_header('last-modified')

        # test book with translator
        book = Book.objects.filter(creator__creator_type__name='Translator').first()
        response = self.client.get(book.get_absolute_url())
        self.assertContains(response, 'Translator')
        self.assertContains(response, book.translators().first().authorized_name)

        # test book with editor, language, subject
        book = Book.objects.filter(creator__creator_type__name='Editor',
                                   languages__isnull=False).first()
        response = self.client.get(book.get_absolute_url())
        self.assertContains(response, 'Editor')
        self.assertContains(response, book.editors().first().authorized_name)
        self.assertContains(response, 'Book Language')
        self.assertContains(response, book.languages.all().first().name)
        self.assertContains(response, 'Book Subject')
        self.assertContains(response, book.subjects.all().first().name)

        # test book with person/book interaction
        book = Book.objects.filter(personbook__isnull=False).first()
        response = self.client.get(book.get_absolute_url())
        self.assertContains(response, 'Person/Book interactions')
        personbook_rel = book.personbook_set.first()
        self.assertContains(response, personbook_rel.person.authorized_name)
        self.assertContains(response, personbook_rel.relationship_type.name)

        # bogus id should 404
        response = self.client.get(reverse('books:detail', args=['foo']))
        assert response.status_code == 404
