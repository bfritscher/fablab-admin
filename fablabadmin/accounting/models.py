# -*- coding: utf-8 -*-
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.utils.translation import ugettext_lazy as _
from fablabadmin.base.models import Invoice
import re

# CRDT
# VIREMENT DU COMPTE (compte) (nom adresse) [EXPÉDITEUR: (nom adresse)] [COMMUNICATIONS: (text)]
virement_du_compte = re.compile(r"VIREMENT DU COMPTE ([\d-]*) (.*?)(?: EXPÉDITEUR: (.*?))?(?: COMMUNICATIONS: (.*?))?$")

# VIREMENT DE SIC ONLINE (SIC_IID) DONNEUR D'ORDRE: (nom) (iban) [COMMUNICATIONS: (text)]
virement_de_sic = re.compile(r"VIREMENT DE SIC ONLINE ([\d]*) DONNEUR D'ORDRE: (.*?)( [\dA-Z]+)(?: COMMUNICATIONS: (.*?))$")

# DBIT
# E-FINANCE (compte) nom [(iban) (nom adresse)]
e_finance = re.compile(r"E-FINANCE ([\d-]*) (.*?)(?:( [\dA-Z]{20,34} )(.*?))?$")

@python_2_unicode_compatible
class BankTransaction(models.Model):
    DEBIT = 'DBIT'
    CREDIT = 'CRDT'
    TYPE_CHOICES = (
        (DEBIT, _('Debit')),
        (CREDIT, _('Credit')),
    )

    iban = models.CharField(max_length=34, verbose_name=_("iban"), blank=False, null=False)
    transaction_id = models.CharField(max_length=200, verbose_name=_("transaction id"), blank=False, null=False)
    currency = models.CharField(max_length=3, verbose_name=_("currency"), blank=False, null=False)
    amount = models.DecimalField(verbose_name=_("amount"), default=0, blank=False, decimal_places=2, max_digits=10)
    type = models.CharField(choices=TYPE_CHOICES, default=CREDIT, max_length=4, verbose_name=_("type"), blank=False, null=False)
    booking_date = models.DateField(verbose_name=_("booking date"))
    raw_text = models.TextField(verbose_name=_("raw text"), blank=True, null=False)
    comment = models.TextField(verbose_name=_("comment"), blank=True, null=False)
    counterpart_account = models.CharField(max_length=50, verbose_name=_("counterpart account"), blank=True, null=True)
    invoice = models.ForeignKey(Invoice, null=True, blank=True, verbose_name=_("invoice"), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _("bank transaction")
        verbose_name_plural = _("bank transactions")
        ordering = ('-booking_date',)
        unique_together = (("iban", "transaction_id"),)

    def __str__(self):
        return u'%s %s %s %s %s' % (self.iban, self.transaction_id, self.booking_date, self.amount, self.currency)

    @property
    def details(self):
        m = None
        o = BankTransactionDetail()
        o.type = 'NONE'
        if self.type == BankTransaction.CREDIT:
            m = virement_du_compte.match(self.raw_text)
            if m is not None:
                res = m.groups()
                o.type = 'COMPTE'
                o.account = res[0]
                o.contact = res[1]
                o.sender = res[2]
                o.message = res[3]
            else:
                m = virement_de_sic.match(self.raw_text)
                if m is not None:
                    res = m.groups()
                    o.type = 'SIC'
                    o.sic_iid = res[0]
                    o.contact = res[1]
                    o.iban = res[2]
                    o.message = res[3]

        if self.type == BankTransaction.DEBIT:
            m = e_finance.match(self.raw_text)
            if m is not None:
                res = m.groups()
                o.type = 'E_FINANCE'
                o.account = res[0]
                o.iban = res[1]
                o.contact = res[2]

        return o

    details.fget.short_description = _("details")


@python_2_unicode_compatible
class BankTransactionDetail(object):
    def items(self):
        return self.__dict__.iteritems()

    def __str__(self):
        s = u""
        for attr, value in self.__dict__.iteritems():
            s += u"%s: %s\n" % (attr, value)
        return s