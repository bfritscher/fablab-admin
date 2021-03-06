# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-08-31 20:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0009_invoice_title'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='resourcetype',
            options={'ordering': ('order',), 'verbose_name': 'resource type', 'verbose_name_plural': 'resource types'},
        ),
        migrations.AddField(
            model_name='resourcetype',
            name='order',
            field=models.PositiveIntegerField(db_index=True, default=0, editable=False),
        ),
    ]
