from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required

from winthrop.people.views import ViafAutoSuggest


urlpatterns = [
    url(r'^autocomplete/viaf/suggest/$', staff_member_required(ViafAutoSuggest.as_view()),
        name='viaf-autosuggest'),
]
