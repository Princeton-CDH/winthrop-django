# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-16 13:28

# Code adapted from derrida-django
# derrida/books/migrations/0009_migrate_plum_to_figgy.py

from __future__ import unicode_literals

from django.db import migrations, models
from djiffy.models import IIIFPresentation
from piffle import iiif
import requests

from winthrop.books.management.commands.import_digitaleds \
    import WinthropManifestImporter


def migrate_plum_to_figgy(apps, schema_editor):

    # get models from djiffy and annotation sub module
    Manifest = apps.get_model('djiffy', 'Manifest')
    Canvas = apps.get_model('djiffy', 'Canvas')
    Annotation = apps.get_model('annotation', 'Annotation')

    # update uris
    mnf_importer = WinthropManifestImporter(update=True)

    for db_manif in Manifest.objects.filter(uri__contains='plum.princeton'):
        plum_uri = db_manif.uri
        figgy_uri = plum_uri.replace('https://plum.princeton',
                                     'https://figgy.princeton')
        response = requests.head(figgy_uri)
        # expect a 302; ignore if we got something else
        if not response.status_code == requests.codes.found:
            # Leave this be, but raise an assert error in check
            # for unconverted uris down so that we know the migration did
            # not work as expected
            next

        db_manif.uri = response.headers['location']
        db_manif.short_id = IIIFPresentation.short_id(db_manif.uri)

        # retrieve the manifest from the new url
        newmanif = IIIFPresentation.from_url(response.headers['location'])

        # loop through canvases in the manifest to make a lookup
        # based on short id
        canvas_by_id = {}
        for canvas in newmanif.sequences[0].canvases:
            try:
                canvas_by_id[canvas.local_identifier] = canvas
            except AttributeError:
                pass

        # loop through canvases stored in the database for this manifest
        # and update them
        for index, db_canvas in enumerate(db_manif.canvases.all()):
            # update canvas uri and save in the database
            try:
                db_canvas.uri = canvas_by_id[db_canvas.short_id].id
            except KeyError:
                # if short id lookup fails, map by index
                db_canvas.uri = newmanif.sequences[0].canvases[index].id

            db_canvas.save()

            # NOTE: not updating other canvas metadata here; use
            # existing import/update script once urls have been migrated

        # save the manifest with the new figgy url
        db_manif.save()

        # use standard import/update logic to update everything else
        mnf_importer.import_manifest(newmanif, newmanif.id)

        imgs = []
        figgy_imgs = []
        for ann in Annotation.objects.filter(uri__contains=plum_uri):
            # annotations have a db-association with canvas objects,
            # but also reference canvas URI as annotation target and
            # and IIIF image url in image selection
            old_canvas_id = ann.uri.rsplit('/')[-1]

            # update annotated canvas uri
            new_canvas = canvas_by_id[old_canvas_id]
            ann.uri = new_canvas.id

            # use piffle iiif image handling to update iiif server and
            # image id without modifying other image parameters
            # - parse image selection uri as iiif image
            if 'image_selection' in ann.extra_data:
                img = iiif.IIIFImageClient.init_from_url(ann.extra_data['image_selection']['uri'])
                # - load iiif image service as iiifimage
                figgy_img = iiif.IIIFImageClient(*new_canvas.images[0].resource.service.id.rsplit('/', 1))
                # update existing iiif image url with new server & image id
                img.api_endpoint = figgy_img.api_endpoint
                img.image_id = figgy_img.image_id
                # image uri is stored in two places, so update both
                ann.extra_data['image_selection']['uri'] = str(img)
                ann.extra_data['image_selection']['src'] = str(img)



            ann.save()

    # as a sanity check, in case anything went wrong -
    # check for any unmigrated plum uris and warn if any are found
    unmigrated = {
        'manifest': Manifest.objects.filter(uri__contains='plum.princeton').count(),
        'canvas': Canvas.objects.filter(uri__contains='plum.princeton').count(),
        'intervention': Annotation.objects.filter(models.Q(uri__contains='plum.princeton') |
                                                  models.Q(extra_data__contains='plum.princeton')) \
                                                  .count()
    }
    if any(unmigrated.values()):
        print('Found unmigrated content: %(manifest)d manifests, %(canvas)d canvases, %(intervention)d interventions' %
              unmigrated)
        # This will trigger an error
        assert False


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0014_make_book_slugs_unique'),
    ]

    operations = [
        migrations.RunPython(
            code=migrate_plum_to_figgy,
            reverse_code=migrations.RunPython.noop,
        )
    ]
