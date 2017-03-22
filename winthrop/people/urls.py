from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required

from winthrop.people.views import ViafAutoSuggest, PersonAutocomplete


urlpatterns = [
    url(r'^autocomplete/$', staff_member_required(PersonAutocomplete.as_view()),
        name='autocomplete'),
    url(r'^autocomplete/viaf/suggest/$', staff_member_required(ViafAutoSuggest.as_view()),
        name='viaf-autosuggest'),
    url(r'^autocomplete/person/$', staff_member_required(PersonAutocomplete.as_view()),
        name='autocomplete'),
]
