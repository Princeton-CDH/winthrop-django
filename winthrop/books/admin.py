from django.contrib import admin

from .models import Subject, Language, Publisher, OwningInstitution, \
    Book, Catalogue, BookSubject, BookLanguage, CreatorType, Creator, \
    PersonBook


admin.site.register(Subject)
admin.site.register(Language)
admin.site.register(Publisher)
admin.site.register(OwningInstitution)
admin.site.register(Book)
admin.site.register(Catalogue)
admin.site.register(CreatorType)
# NOTE: these will probably be inlines, but register for testing for now
admin.site.register(BookSubject)
admin.site.register(BookLanguage)
admin.site.register(Creator)
admin.site.register(PersonBook)