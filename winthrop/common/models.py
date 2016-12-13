from django.db import models

# abstract models with common fields to be
# used as mix-ins

class Named(models.Model):
    '''Abstract model with a 'name' field; by default, name is used as
    the string display.'''
    name = models.CharField(max_length=255)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Notable(models.Model):
    '''Abstract model with an optional notes text field'''
    notes = models.TextField(blank=True)

    class Meta:
        abstract = True



