# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-12 19:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contact',
            options={'ordering': ('first_name', 'last_name'), 'verbose_name': 'contact', 'verbose_name_plural': 'contacts'},
        ),
        migrations.AddField(
            model_name='resource',
            name='price',
            field=models.FloatField(blank=True, null=True, verbose_name='usage price'),
        ),
        migrations.AddField(
            model_name='resource',
            name='price_unit',
            field=models.CharField(default=b'', max_length=10, verbose_name='price unit'),
        ),
        migrations.AlterField(
            model_name='function',
            name='name',
            field=models.CharField(max_length=60, verbose_name='function name'),
        ),
    ]
