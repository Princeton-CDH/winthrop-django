from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required

from winthrop.annotation.views import TagAutocomplete


urlpatterns = [
    url(r'^autocomplete/tag/$',
        staff_member_required(TagAutocomplete.as_view()), name='tag-autocomplete'),
]
