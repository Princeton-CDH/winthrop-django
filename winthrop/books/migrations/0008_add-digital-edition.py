# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-17 18:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('djiffy', '0001_initial'),
        ('books', '0007_title-length'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='book',
            options={'ordering': ['title']},
        ),
        migrations.AddField(
            model_name='book',
            name='digital_edition',
            field=models.ForeignKey(blank=True, help_text='Digitized edition of this book, if available', null=True, on_delete=django.db.models.deletion.CASCADE, to='djiffy.Manifest'),
        ),
    ]
