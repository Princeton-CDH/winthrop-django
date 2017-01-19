from django.db import models

from winthrop.common.models import Named, Notable


class Place(Named, Notable):
    # store full geonames uri
    geonames_id = models.URLField()
    latitude = models.FloatField()
    longitude = models.FloatField()


