import autocomplete_light
from django.contrib.admin import ModelAdmin
from django.contrib import admin

from fablabadmin.base.models import Invoice
from .models import BankTransaction


@admin.register(BankTransaction)
class BankTransactionAdmin(ModelAdmin):
    date_hierarchy = 'booking_date'
    readonly_fields =  ['iban', 'transaction_id', 'details']
    form = autocomplete_light.modelform_factory(BankTransaction, fields='__all__')
    fields = (('iban', 'transaction_id'), 'booking_date', ('amount', 'currency'), 'type', ('raw_text', 'details'), 'invoice', 'counterpart_account', 'comment')
    list_display = ('__str__', 'booking_date', 'amount', 'invoice')
