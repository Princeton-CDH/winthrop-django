from django.db import models

from winthrop.common.models import Named, Notable


class Place(Named, Notable):
    # do we want to store id only or geonames uri?
    geonames_id = models.PositiveIntegerField()

