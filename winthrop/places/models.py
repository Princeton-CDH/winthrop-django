from django.db import models


class Place(models.Model):
    name = models.CharField(max_length=255)
    # do we want to store id only or geonames uri?
    geonames_id = models.PositiveIntegerField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name