from django.core.management.base import BaseCommand
from djiffy.importer import ManifestImporter

from winthrop.books.models import Book


class WinthropManifestImporter(ManifestImporter):
    '''Extends :class:`djiffy.importer.ManifestImporter` to add additional
    logic for associating the imported :class:`djiffy.models.Manifest`
    with an existing :class:`winthrop.books.models.Book`'''

    def import_book(self, manifest, path):
        # parent method returns newly created db manifest
        # or None if there was an error or manifest was already imported
        db_manifest = super(WinthropManifestImporter, self) \
            .import_book(manifest, path)
        if not db_manifest:
            return

        # attempt to find the corresponding Winthrop book object
        # for this digital edition and associate them
        # - edited NYSL winthrop volumes in Plum will have a winthrop
        #   call number set as a local identifier
        if 'Local identifier' in db_manifest.metadata:
            winthrop_num = db_manifest.metadata['Local identifier'][0]
            books = Book.objects.filter(catalogue__call_number=winthrop_num)
            # only associate if one and only one match is found
            if books.count() == 1:
                book = books.first()
                book.digital_edition = db_manifest
                book.save()

            else:
                self.error_msg('No match for %s' % winthrop_num)

        else:
            self.error_msg('No local identifier found')

        return db_manifest

class Command(BaseCommand):
    '''Import digital editions and associate with Winthrop books'''
    help = __doc__

    # shorthand for known URIs to be imported
    manifest_uris = {
        'NYSL': 'https://plum.princeton.edu/collections/p4j03fz143/manifest'
    }

    def add_arguments(self, parser):
        parser.add_argument('path', nargs='+',
            help='''One or more IIIF Collections or Manifests as file or URL.
            Use 'NYSL' to import PUL NYSL materials.''')

    def handle(self, *args, **kwargs):
        # convert any shorthand ids into the appropriate manifest uri
        manifest_paths = [self.manifest_uris[p] if p in self.manifest_uris else p
                          for p in kwargs['path']]
        WinthropManifestImporter(stdout=self.stdout, stderr=self.stderr,
                                 style=self.style) \
            .import_paths(manifest_paths)


