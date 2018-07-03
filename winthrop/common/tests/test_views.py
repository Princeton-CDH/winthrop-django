from datetime import datetime
from django.test import TestCase

from winthrop.common.views import LastModifiedMixin


class TestLastModifiedMixin(TestCase):

    def test_solr_timestamp_to_datetime(self):
        # with microseconds
        solr_dt = LastModifiedMixin.solr_timestamp_to_datetime('2018-07-02T21:08:46.428Z')
        assert solr_dt == datetime(2018, 7, 2, 21, 8, 46)
        # without
        solr_dt = LastModifiedMixin.solr_timestamp_to_datetime('2018-07-02T21:08:46Z')
        assert solr_dt == datetime(2018, 7, 2, 21, 8, 46)


