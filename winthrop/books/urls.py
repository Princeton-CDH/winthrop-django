from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required

from winthrop.books.views import PublisherAutocomplete, CanvasAutocomplete, \
    LanguageAutocomplete, SubjectAutocomplete


urlpatterns = [
    url(r'^autocomplete/publisher/$', staff_member_required(PublisherAutocomplete.as_view()),
        name='publisher-autocomplete'),
    url(r'^canvas/publisher/$', staff_member_required(CanvasAutocomplete.as_view()),
        name='canvas-autocomplete'),
    url(r'^autocomplete/language/$', staff_member_required(LanguageAutocomplete.as_view()),
        name='language-autocomplete'),
    url(r'^autocomplete/subject/$', staff_member_required(SubjectAutocomplete.as_view()),
        name='subject-autocomplete'),
]
