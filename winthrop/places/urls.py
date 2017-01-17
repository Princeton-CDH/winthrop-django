from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required

from winthrop.places.views import PlaceAutocomplete


urlpatterns = [
    url(r'^autocomplete/$', staff_member_required(PlaceAutocomplete.as_view()),
        name='place-autocomplete',
    ),
]