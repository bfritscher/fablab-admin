from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from redactor.fields import RedactorField
import datetime

class ContactStatus(models.Model):
    name = models.CharField(_('name'), max_length=30, blank=False, null=False)

    class Meta:
        verbose_name = _("contact status")
        verbose_name_plural = _("contact statuses")

    def __str__(self):
        return self.name


class ResourceType(models.Model):
    name = models.CharField(max_length=60, verbose_name=_("name"), blank=False, null=False)

    def __str__(self):
        return self.name


class Contact(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True, null=False)
    last_name = models.CharField(_('last name'), max_length=30, blank=True, null=False)
    email = models.EmailField(_('email address'), blank=True, null=False)
    status = models.ForeignKey(ContactStatus, verbose_name=_("status"), on_delete=models.PROTECT)
    address = models.CharField(verbose_name=_("address"), max_length=200, blank=True, null=False)
    postal_code = models.CharField(verbose_name=_("postal code"), max_length=10, blank=True, null=False)
    city = models.CharField(verbose_name=_("city"), max_length=200, blank=True, null=False)
    country = models.CharField(verbose_name=_("country"), max_length=200, blank=True, null=False)
    phone = models.CharField(verbose_name=_("phone"), max_length=30, blank=True, null=False)
    birth_year = models.PositiveIntegerField(verbose_name=_("year of birth"), blank=True, null=True)
    comment = models.TextField(verbose_name=_("comment"), blank=True, null=False)
    education = models.CharField(verbose_name=_("education"), max_length=200, blank=True, null=False)
    profession = models.CharField(verbose_name=_("profession"), max_length=200, blank=True, null=False)
    employer = models.CharField(verbose_name=_("employer"), max_length=200, blank=True, null=False)
    interests = models.TextField(verbose_name=_("interests"), blank=True, null=False)
    payment_info = models.TextField(verbose_name=_("payment information"), blank=True, null=False)
    trainings = models.ManyToManyField(ResourceType, through="Training")

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)


# sync contact to user
@receiver(post_save, sender=Contact, dispatch_uid="update_user")
def update_user(sender, instance, **kwargs):
    contact = instance
    if contact.user:
        contact.user.first_name = contact.first_name
        contact.user.last_name = contact.last_name
        contact.user.email = contact.email
        contact.user.save()


class Function(models.Model):
    member = models.ForeignKey(Contact, related_name="functions", verbose_name=_("member"), on_delete=models.CASCADE) #limit_choices_to={'is_staff': True},
    name = models.CharField(max_length=60, verbose_name=_("name"), blank=False, null=False)
    year_from = models.PositiveIntegerField(verbose_name=_("year started"), blank=False, null=False)
    year_to = models.PositiveIntegerField(verbose_name=_("year ended"), blank=True, null=True)

    class Meta:
        verbose_name = _("function")
        verbose_name_plural = _("functions")
        ordering = ['-year_from']

    def __str__(self):
        full_name = '%s %s - %s' % (self.name, self.year_from, self.year_to or '')
        return full_name.strip()


class Resource(models.Model):
    name = models.CharField(max_length=60, verbose_name=_("name"), blank=False, null=False)
    type = models.ForeignKey(ResourceType, related_name="resources", verbose_name=_("type"), on_delete=models.PROTECT)
    description = RedactorField(verbose_name=_("description"), blank=True, null=False)

    def __str__(self):
        return '%s | %s' % (self.type, self.name)


class Training(models.Model):
    member = models.ForeignKey(Contact, verbose_name=_("member"), on_delete=models.CASCADE)
    resource = models.ForeignKey(ResourceType, verbose_name=_("resource"), on_delete=models.CASCADE)
    date = models.DateField(verbose_name=_("date"))

    def __str__(self):
        return '%s - %s' % (self.resource, self.member)


class Invoice(models.Model):
    INVOICE_TYPE = (
        ("E", _("expense")),
        ("I", _("income"))
    )
    PAYMENT_TYPE = (
        ("C", _("cash")),
        ("B", _("bank"))
    )
    date = models.DateField(verbose_name=_("date"))
    buyer = models.ForeignKey(Contact, verbose_name=_("buyer"), related_name="invoices", on_delete=models.PROTECT)
    seller = models.ForeignKey(Contact, verbose_name=_("seller"), related_name="expenses", on_delete=models.PROTECT)
    paid = models.DateField(verbose_name=_("date paid"), blank=True, null=True)
    payment_type = models.CharField(max_length=1, choices=PAYMENT_TYPE, default="B")
    type = models.CharField(max_length=1, choices=INVOICE_TYPE, default="I")
    document = models.FileField(verbose_name=_("document"), blank=True, null=True)

    def __str__(self):
        return '%s %s' % (_(dict(self.INVOICE_TYPE)[self.type]).capitalize(), self.id)


class LedgerEntry(models.Model):

    LEDGER_TYPE = (
        ("D", _("debit")),
        ("C", _("credit"))
    )

    date = models.DateField(verbose_name=_("date"))
    title = models.CharField(max_length=100, verbose_name=_("title"), blank=True, null=True)
    description = models.TextField(verbose_name=_("description"), blank=False, null=False)
    quantity = models.FloatField(verbose_name=_("quantity"), blank=False, default=1)
    unit_price = models.FloatField(verbose_name=_("unit price"), blank=False, default=0)
    user = models.ForeignKey(Contact, verbose_name=_("member"), related_name="ledger_entries", blank=True, null=True, on_delete=models.PROTECT)
    invoice = models.ForeignKey(Invoice, verbose_name=_("invoice"), related_name="entries", blank=True, null=True)

    @property
    def total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return _("Transaction on %(date)s for %(total)s by %(user)s") % {'user': self.user, 'total':self.total, 'date': self.date}

    class Meta:
        verbose_name_plural = _("ledger entries")


def current_year():
    now = datetime.datetime.now()
    return now.year


class MembershipInvoice(LedgerEntry):
    year = models.PositiveIntegerField(verbose_name=_("year"), default=current_year)
    # TODO: auto create invoice

    def __str__(self):
        return _("Membership %(year)s for %(user)s") % {'user': self.user, 'year': self.year}


class ResourceUsage(LedgerEntry):
    resource = models.ForeignKey(Resource, verbose_name=_("resource"), related_name="usages", on_delete=models.PROTECT)

    def __str__(self):
        return _("Usage of %(resource)s by %(user)s") % {'user': self.user, 'resource': self.resource}


class Event(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("title"))
    start_date = models.DateField(verbose_name=_("start date"))
    end_date = models.DateField(verbose_name=_("end date"), blank=True, null=True)
    description = RedactorField(verbose_name=_("description"), blank=True, null=False)
    max_participants = models.PositiveIntegerField(verbose_name=_("maximum number of participants"), default=0)
    organizers = models.ManyToManyField(Contact)

    def __str__(self):
        txt = "%s (%s" % (self.title, self.start_date)
        if self.end_date:
            txt += " - %s" % (self.end_date,)
        return txt + ")"


class EventRegistration(LedgerEntry):
    event = models.ForeignKey(Event, verbose_name=_("event"), related_name="registrations", on_delete=models.PROTECT)

    def __str__(self):
        return _("Registration to %(event)s by %(user)s") % {'user': self.user, 'event': self.event}


class Expense(LedgerEntry):
    event = models.ForeignKey(Event, verbose_name=_("event"), related_name="expenses", blank=True, null=True, on_delete=models.PROTECT)
    contact = models.ForeignKey(Contact, verbose_name=_("provider"), blank=True, null=True, on_delete=models.PROTECT)
    document = models.FileField(verbose_name=_("document"), blank=True, null=True)

    def __str__(self):
        return _("Expense for %(expense)s by %(user)s") % {'user': self.user, 'expense': self.title}
