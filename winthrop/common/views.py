from datetime import datetime

from django.utils.cache import get_conditional_response
from django.views.generic.base import View


# last modified view mixins borrowed from cdhweb

class LastModifiedMixin(View):

    def last_modified(self):
        # for single-object displayable
        return self.get_object().updated

    def dispatch(self, request, *args, **kwargs):
        response = super(LastModifiedMixin, self).dispatch(request, *args, **kwargs)
        # NOTE: remove microseconds so that comparison will pass,
        # since microseconds are not included in the last-modified header

        last_modified = self.last_modified()
        if last_modified:
            last_modified = self.last_modified().replace(microsecond=0)
            response['Last-Modified'] = last_modified.strftime('%a, %d %b %Y %H:%M:%S GMT')
            last_modified = last_modified.timestamp()

        return get_conditional_response(
            request, last_modified=last_modified, response=response)

    @staticmethod
    def solr_timestamp_to_datetime(solr_time):
        # Solr stores date in isoformat; convert to datetime object
        # - microseconds only included when second is not exact; strip out if
        #    they are present
        print(solr_time)
        if '.' in solr_time:
            solr_time = '%sZ' % solr_time.split('.')[0]
        return datetime.strptime(solr_time, '%Y-%m-%dT%H:%M:%SZ')


class LastModifiedListMixin(LastModifiedMixin):

    def last_modified(self):
        # for list object displayable; assumes django queryset
        queryset = self.get_queryset()
        if queryset.exists():
            return queryset.order_by('updated').first().updated
