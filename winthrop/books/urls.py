from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required

from winthrop.books import views


urlpatterns = [
    url(r'^$', views.BookListView.as_view(), name='list'),
    url(r'^facets/$', views.BookFacetJSONView.as_view(), name='facets'),
    url(r'^(?P<slug>[-\w]+)/$', views.BookDetailView.as_view(), name='detail'),
    url(r'^(?P<slug>[-\w]+)/pages/$', views.BookPageView.as_view(), name='pages'),
    url(r'^autocomplete/publisher/$', staff_member_required(views.PublisherAutocomplete.as_view()),
        name='publisher-autocomplete'),
    url(r'^autocomplete/canvas/$', staff_member_required(views.CanvasAutocomplete.as_view()),
        name='canvas-autocomplete'),
    url(r'^autocomplete/language/$', staff_member_required(views.LanguageAutocomplete.as_view()),
        name='language-autocomplete'),
    url(r'^autocomplete/subject/$', staff_member_required(views.SubjectAutocomplete.as_view()),
        name='subject-autocomplete'),
]
