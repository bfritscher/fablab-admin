# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-05-08 07:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_fix_relations'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='external_reference',
            field=models.TextField(blank=True, default=b'', verbose_name='external reference'),
        ),
        migrations.AddField(
            model_name='ledgerentry',
            name='external_reference',
            field=models.TextField(blank=True, default=b'', verbose_name='external reference'),
        ),
    ]
