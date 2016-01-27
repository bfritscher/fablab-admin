from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from redactor.fields import RedactorField
from filer.fields.file import FilerFileField
import datetime
from polymorphic.models import PolymorphicModel
from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible
class ContactStatus(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=30, blank=False, null=False)
    is_member = models.BooleanField(verbose_name=_("is member"), default=False)

    class Meta:
        verbose_name = _("contact status")
        verbose_name_plural = _("contact statuses")

    def __str__(self):
        return self.name

@python_2_unicode_compatible
class ResourceType(models.Model):
    name = models.CharField(max_length=60, verbose_name=_("name"), blank=False, null=False)

    def __str__(self):
        return self.name

@python_2_unicode_compatible
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

    def is_membership_paid(self):
        m = MembershipInvoice.objects.filter(user=self, year=datetime.date.today().year).first()
        if m:
            if m.invoice:
                return m.invoice.paid
            else:
                return None
        return False
    is_membership_paid.short_description = _('is %(year)s membership paid') % {'year': datetime.date.today().year}

    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)
    full_name.short_description = _('full name')

    def __str__(self):
        return self.full_name()


# sync contact to user
@receiver(post_save, sender=Contact, dispatch_uid="update_user")
def update_user(sender, instance, **kwargs):
    contact = instance
    if contact.user:
        contact.user.first_name = contact.first_name
        contact.user.last_name = contact.last_name
        contact.user.email = contact.email
        contact.user.save()

@python_2_unicode_compatible
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


@python_2_unicode_compatible
class Resource(models.Model):
    name = models.CharField(max_length=60, verbose_name=_("name"), blank=False, null=False)
    type = models.ForeignKey(ResourceType, related_name="resources", verbose_name=_("type"), on_delete=models.PROTECT)
    description = RedactorField(verbose_name=_("description"), blank=True, null=False)

    def __str__(self):
        return '%s | %s' % (self.type, self.name)


@python_2_unicode_compatible
class Training(models.Model):
    member = models.ForeignKey(Contact, verbose_name=_("member"), on_delete=models.CASCADE)
    resource = models.ForeignKey(ResourceType, verbose_name=_("resource"), on_delete=models.CASCADE)
    date = models.DateField(verbose_name=_("date"))

    def __str__(self):
        return '%s - %s' % (self.resource, self.member)


@python_2_unicode_compatible
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
    draft = models.BooleanField(verbose_name=_("draft"), default=True)
    total = models.IntegerField(verbose_name=_("total"), default=0)
    document = models.FileField(verbose_name=_("document"), blank=True, null=True)

    def __str__(self):
        return '%s %s' % (_(dict(self.INVOICE_TYPE)[self.type]).capitalize(), self.id)


@python_2_unicode_compatible
class LedgerEntry(PolymorphicModel):

    LEDGER_TYPE = (
        ("D", _("debit")),
        ("C", _("credit"))
    )

    date = models.DateField(verbose_name=_("date"), default=datetime.date.today)
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


@python_2_unicode_compatible
class MembershipInvoice(LedgerEntry):
    year = models.PositiveIntegerField(verbose_name=_("year"), default=current_year)
    # TODO: auto create invoice

    def is_membership_paid(self):
        if self.invoice:
            return self.invoice.paid
        return False
    is_membership_paid.short_description = _('is membership paid')

    def save(self):
        self.quantity = 1
        if not self.title or self.title is None:
            self.title = _('Membership')

        if not self.description or self.description is None:
            self.description = _('membership %(year)s') % {'year': self.year}

        if self.invoice is None:
            seller = Contact.objects.filter(status__name='fablab_invoice').first()
            self.invoice = Invoice.objects.create(total=self.unit_price,
                                                  date=self.date,
                                                  buyer=self.user,
                                                  seller=seller,
                                                  draft=False
                                                  )

        super(MembershipInvoice, self).save()
        #save invoice

    def __str__(self):
        return _("Membership %(year)s for %(user)s") % {'user': self.user, 'year': self.year}


@python_2_unicode_compatible
class ResourceUsage(LedgerEntry):
    resource = models.ForeignKey(Resource, verbose_name=_("resource"), related_name="usages", on_delete=models.PROTECT)

    def __str__(self):
        return _("Usage of %(resource)s by %(user)s") % {'user': self.user, 'resource': self.resource}


@python_2_unicode_compatible
class Event(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("title"))
    start_date = models.DateField(verbose_name=_("start date"))
    end_date = models.DateField(verbose_name=_("end date"), blank=True, null=True)
    location = models.TextField(verbose_name=_("location"), blank=True)
    description = RedactorField(verbose_name=_("description"), blank=True)
    min_participants = models.PositiveIntegerField(verbose_name=_("minimum number of participants"), default=0)
    max_participants = models.PositiveIntegerField(verbose_name=_("maximum number of participants"), default=0)
    organizers = models.ManyToManyField(Contact)

    def __str__(self):
        txt = "%s (%s" % (self.title, self.start_date)
        if self.end_date:
            txt += " - %s" % (self.end_date,)
        return txt + ")"


@python_2_unicode_compatible
class EventDocument(models.Model):
    file = FilerFileField(verbose_name=_("document"), related_name="event_document")
    event = models.ForeignKey(Event, related_name="documents", verbose_name=_("event"))

    def __str__(self):
        return self.file.label.encode('utf-8')


@python_2_unicode_compatible
class EventRegistration(LedgerEntry):
    event = models.ForeignKey(Event, verbose_name=_("event"), related_name="registrations", on_delete=models.PROTECT)

    def __str__(self):
        return _("Registration to %(event)s by %(user)s") % {'user': self.user, 'event': self.event}


@python_2_unicode_compatible
class Expense(LedgerEntry):
    event = models.ForeignKey(Event, verbose_name=_("event"), related_name="expenses", blank=True, null=True, on_delete=models.PROTECT)
    contact = models.ForeignKey(Contact, verbose_name=_("provider"), blank=True, null=True, on_delete=models.PROTECT)
    document = models.FileField(verbose_name=_("document"), blank=True, null=True)

    def __str__(self):
        return _("Expense for %(expense)s by %(user)s") % {'user': self.user, 'expense': self.title}
