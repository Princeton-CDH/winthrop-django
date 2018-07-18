from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required

from winthrop.books.views import PublisherAutocomplete, CanvasAutocomplete, \
    LanguageAutocomplete, SubjectAutocomplete, BookListView, BookDetailView, \
    BookFacetJSONView


urlpatterns = [
    url(r'^$', BookListView.as_view(), name='list'),
    url(r'^facets/$', BookFacetJSONView.as_view(), name='facets'),
    url(r'^(?P<slug>[-\w]+)/$', BookDetailView.as_view(), name='detail'),
    url(r'^autocomplete/publisher/$', staff_member_required(PublisherAutocomplete.as_view()),
        name='publisher-autocomplete'),
    url(r'^autocomplete/canvas/$', staff_member_required(CanvasAutocomplete.as_view()),
        name='canvas-autocomplete'),
    url(r'^autocomplete/language/$', staff_member_required(LanguageAutocomplete.as_view()),
        name='language-autocomplete'),
    url(r'^autocomplete/subject/$', staff_member_required(SubjectAutocomplete.as_view()),
        name='subject-autocomplete'),
]
