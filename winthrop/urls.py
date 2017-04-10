"""winthrop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
"""
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic.base import RedirectView
from annotator_store import views as annotator_views
from winthrop.annotation.views import TagAutocomplete


urlpatterns = [
    # for now, since there is not yet any public-facing site,
    # redirect base url to admin index page
    url(r'^$', RedirectView.as_view(url='/iiif-books/'), name='site-index'),
    # # grappelli URLS for admin related lookups & autocompletes
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('pucas.cas_urls')),
    url(r'^people/', include('winthrop.people.urls', namespace='people')),
    url(r'^places/', include('winthrop.places.urls', namespace='places')),
    url(r'^books/', include('winthrop.books.urls', namespace='books')),
    url(r'^iiif-books/', include('djiffy.urls', namespace='djiffy')),
    # annotations
    url(r'^annotations/api/', include('annotator_store.urls', namespace='annotation-api')),
    # annotatorjs doesn't handle trailing slash in api prefix url
    url(r'^annotations/api', annotator_views.AnnotationIndex.as_view(), name='annotation-api-prefix'),
    url(r'^annotations/autocomplete/tag/$', staff_member_required(TagAutocomplete.as_view()), name='tag-autocomplete'),
]

if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns += url(r'^__debug__/', include(debug_toolbar.urls)),
    except ImportError:
        pass
