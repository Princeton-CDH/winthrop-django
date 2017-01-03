# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-03 14:13
from __future__ import unicode_literals

from django.core.management import call_command
from django.db import migrations


def load_fixture(apps, schema_editor):
        call_command(
                'loaddata',
                'initial_personbookrelationshiptypes',
                app_label='books'
        )


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0004_auto_20161229_1901'),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=migrations.RunPython.noop),
    ]
