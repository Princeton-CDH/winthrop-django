from datetime import datetime
import json
from time import sleep

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from djiffy.models import Manifest
import pytest

from winthrop.books.models import Book
from winthrop.common.solr import Indexable, PagedSolrQuery


class TestBookViews(TestCase):
    fixtures = ['sample_book_data.json']

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
                self.assertContains(response, creator.person.authorized_name)

        # annotated badge should be displayed for books marked as annotated
        annotated_count = books.filter(is_annotated=True).count()
        self.assertContains(response, '<div class="ui label">annotated</div>',
                            count=annotated_count)

        # associate digital edition & thumbnail from fixture
        book = books.first()
        book.digital_edition = Manifest.objects.first()
        canvas = book.digital_edition.canvases.first()
        canvas.thumbnail = True
        canvas.save()
        # add to Solr index
        book.index(params={'commitWithin': 500})
        sleep(2)

        response = self.client.get(url)
        # should include image urls (1x/2x)
        self.assertContains(response, str(canvas.image.size(height=218)))
        self.assertContains(response, str(canvas.image.size(height=436)))
        # should include image label
        self.assertContains(response, canvas.label)
