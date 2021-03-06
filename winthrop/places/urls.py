from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required

from winthrop.places.views import PlaceAutocomplete, GeonamesLookup


urlpatterns = [
    url(r'^autocomplete/$', staff_member_required(PlaceAutocomplete.as_view()),
        name='autocomplete'),
    url(r'^autocomplete/geonames/$',
        staff_member_required(GeonamesLookup.as_view()),
         name='geonames-autocomplete')
]
