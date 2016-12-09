from django.contrib import admin

from .models import Person, Residence, RelationshipType, Relationship

admin.site.register(Person)
admin.site.register(Residence)
admin.site.register(RelationshipType)
admin.site.register(Relationship)

