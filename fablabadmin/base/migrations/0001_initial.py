# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-31 22:09
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import fablabadmin.base.models
import filer.fields.file
import redactor.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('filer', '0002_auto_20150606_2003'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('address', models.CharField(blank=True, max_length=200, verbose_name='address')),
                ('postal_code', models.CharField(blank=True, max_length=10, verbose_name='postal code')),
                ('city', models.CharField(blank=True, max_length=200, verbose_name='city')),
                ('country', models.CharField(blank=True, max_length=200, verbose_name='country')),
                ('phone', models.CharField(blank=True, max_length=30, verbose_name='phone')),
                ('birth_year', models.PositiveIntegerField(blank=True, null=True, verbose_name='year of birth')),
                ('comment', models.TextField(blank=True, verbose_name='comment')),
                ('education', models.CharField(blank=True, max_length=200, verbose_name='education')),
                ('profession', models.CharField(blank=True, max_length=200, verbose_name='profession')),
                ('employer', models.CharField(blank=True, max_length=200, verbose_name='employer')),
                ('interests', models.TextField(blank=True, verbose_name='interests')),
                ('payment_info', models.TextField(blank=True, verbose_name='payment information')),
            ],
            options={
                'verbose_name': 'contact',
                'verbose_name_plural': 'contacts',
            },
        ),
        migrations.CreateModel(
            name='ContactStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='name')),
                ('is_member', models.BooleanField(default=False, verbose_name='is member')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'contact status',
                'verbose_name_plural': 'contact statuses',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('start_date', models.DateField(verbose_name='start date')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='end date')),
                ('location', models.TextField(blank=True, verbose_name='location')),
                ('description', redactor.fields.RedactorField(blank=True, verbose_name='description')),
                ('website', models.URLField(blank=True, verbose_name='website')),
                ('trello', models.URLField(blank=True, verbose_name='trello')),
                ('min_participants', models.PositiveIntegerField(default=0, verbose_name='minimum number of participants')),
                ('max_participants', models.PositiveIntegerField(default=0, verbose_name='maximum number of participants')),
                ('organizers', models.ManyToManyField(blank=True, null=True, to='base.Contact')),
            ],
            options={
                'verbose_name': 'event',
                'verbose_name_plural': 'events',
            },
        ),
        migrations.CreateModel(
            name='EventDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='base.Event', verbose_name='event')),
                ('file', filer.fields.file.FilerFileField(on_delete=django.db.models.deletion.CASCADE, related_name='event_document', to='filer.File', verbose_name='document')),
            ],
            options={
                'verbose_name': 'event document',
                'verbose_name_plural': 'event documents',
            },
        ),
        migrations.CreateModel(
            name='Function',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60, verbose_name='name')),
                ('year_from', models.PositiveIntegerField(verbose_name='year started')),
                ('year_to', models.PositiveIntegerField(blank=True, null=True, verbose_name='year ended')),
                ('committee', models.BooleanField(default=True, verbose_name='committee')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='functions', to='base.Contact', verbose_name='member')),
            ],
            options={
                'ordering': ['-year_from'],
                'verbose_name': 'function',
                'verbose_name_plural': 'functions',
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date.today, verbose_name='date')),
                ('paid', models.DateField(blank=True, null=True, verbose_name='date paid')),
                ('payment_type', models.CharField(choices=[(b'C', 'cash'), (b'B', 'bank')], default=b'B', max_length=1)),
                ('type', models.CharField(choices=[(b'E', 'expense'), (b'I', 'invoice')], default=b'I', max_length=1)),
                ('draft', models.BooleanField(default=True, verbose_name='draft')),
                ('manual_total', models.FloatField(blank=True, null=True, verbose_name='manual total')),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='invoices', to='base.Contact', verbose_name='buyer')),
                ('document', filer.fields.file.FilerFileField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invoice_document', to='filer.File', verbose_name='document')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='expenses', to='base.Contact', verbose_name='seller')),
            ],
            options={
                'verbose_name': 'invoice',
                'verbose_name_plural': 'invoices',
            },
        ),
        migrations.CreateModel(
            name='LedgerEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date.today, verbose_name='date')),
                ('title', models.CharField(blank=True, max_length=100, null=True, verbose_name='title')),
                ('description', models.TextField(verbose_name='description')),
                ('quantity', models.FloatField(default=1, verbose_name='quantity')),
                ('unit_price', models.FloatField(default=0, verbose_name='unit price')),
                ('type', models.CharField(choices=[(b'D', 'debit'), (b'C', 'credit')], default=b'D', max_length=1, verbose_name='type')),
            ],
            options={
                'ordering': ('title', 'date'),
                'verbose_name': 'ledger entry',
                'verbose_name_plural': 'ledger entries',
            },
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60, verbose_name='name')),
                ('description', redactor.fields.RedactorField(blank=True, verbose_name='description')),
            ],
            options={
                'ordering': ('type__name', 'name'),
                'verbose_name': 'resource',
                'verbose_name_plural': 'resources',
            },
        ),
        migrations.CreateModel(
            name='ResourceType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60, verbose_name='name')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'resource type',
                'verbose_name_plural': 'resource types',
            },
        ),
        migrations.CreateModel(
            name='Training',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='date')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Contact', verbose_name='member')),
                ('resource_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.ResourceType', verbose_name='resource type')),
            ],
            options={
                'ordering': ('member__first_name', 'resource_type__name'),
                'verbose_name': 'training',
                'verbose_name_plural': 'trainings',
            },
        ),
        migrations.CreateModel(
            name='EventRegistration',
            fields=[
                ('ledgerentry_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='base.LedgerEntry')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='registrations', to='base.Event', verbose_name='event')),
            ],
            options={
                'verbose_name': 'event registration',
                'verbose_name_plural': 'event registrations',
            },
            bases=('base.ledgerentry',),
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('ledgerentry_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='base.LedgerEntry')),
                ('document', filer.fields.file.FilerFileField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='filer.File', verbose_name='document')),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='expenses', to='base.Event', verbose_name='event')),
            ],
            options={
                'verbose_name': 'expense',
                'verbose_name_plural': 'expenses',
            },
            bases=('base.ledgerentry',),
        ),
        migrations.CreateModel(
            name='MembershipInvoice',
            fields=[
                ('ledgerentry_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='base.LedgerEntry')),
                ('year', models.PositiveIntegerField(default=fablabadmin.base.models.current_year, verbose_name='year')),
            ],
            options={
                'verbose_name': 'membership invoice',
                'verbose_name_plural': 'membership invoices',
            },
            bases=('base.ledgerentry',),
        ),
        migrations.CreateModel(
            name='ResourceUsage',
            fields=[
                ('ledgerentry_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='base.LedgerEntry')),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='resource_usages', to='base.Event', verbose_name='event')),
            ],
            options={
                'verbose_name': 'resource usage',
                'verbose_name_plural': 'resource usages',
            },
            bases=('base.ledgerentry',),
        ),
        migrations.AddField(
            model_name='resource',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='resources', to='base.ResourceType', verbose_name='type'),
        ),
        migrations.AddField(
            model_name='ledgerentry',
            name='invoice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='base.Invoice', verbose_name='invoice'),
        ),
        migrations.AddField(
            model_name='ledgerentry',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_base.ledgerentry_set+', to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='ledgerentry',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ledger_entries', to='base.Contact', verbose_name='member'),
        ),
        migrations.AddField(
            model_name='contact',
            name='status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.ContactStatus', verbose_name='status'),
        ),
        migrations.AddField(
            model_name='contact',
            name='trainings',
            field=models.ManyToManyField(through='base.Training', to='base.ResourceType'),
        ),
        migrations.AddField(
            model_name='contact',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='resourceusage',
            name='resource',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='usages', to='base.Resource', verbose_name='resource'),
        ),
        migrations.AddField(
            model_name='expense',
            name='provider',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='base.Contact', verbose_name='provider'),
        ),
    ]