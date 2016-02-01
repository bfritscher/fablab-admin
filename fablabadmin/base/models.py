from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models, IntegrityError
from django.contrib.auth.models import User
from django.db.models import Sum, F, FloatField, ExpressionWrapper
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from redactor.fields import RedactorField
from filer.fields.file import FilerFileField
import datetime
from polymorphic.models import PolymorphicModel
from django.utils.encoding import python_2_unicode_compatible
import filer.models as filer_models
from django.core.files.base import ContentFile
from fablabadmin.base.utils import *
from django.forms.models import modelform_factory
from fablabadmin.base.utils import send_invoice


@python_2_unicode_compatible
class ContactStatus(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=30, blank=False, null=False)
    is_member = models.BooleanField(verbose_name=_("is member"), default=False)

    class Meta:
        verbose_name = _("contact status")
        verbose_name_plural = _("contact statuses")
        ordering = ('name',)

    def __str__(self):
        return u'%s' % self.name


@python_2_unicode_compatible
class ResourceType(models.Model):
    name = models.CharField(max_length=60, verbose_name=_("name"), blank=False, null=False)

    class Meta:
        verbose_name = _("resource type")
        verbose_name_plural = _("resource types")
        ordering = ('name',)

    def __str__(self):
        return u'%s' % self.name


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
        return u'%s %s' % (self.first_name, self.last_name)
    full_name.short_description = _('full name')

    class Meta:
        verbose_name = _("contact")
        verbose_name_plural = _("contacts")
        ordering = ('first_name', 'last_name')

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

    if contact.status.is_member:
        mailchimp_add(contact)
    else:
        mailchimp_remove(contact)


@python_2_unicode_compatible
class Function(models.Model):
    member = models.ForeignKey(Contact, related_name="functions", verbose_name=_("member"), on_delete=models.CASCADE) #limit_choices_to={'is_staff': True},
    name = models.CharField(max_length=60, verbose_name=_("name"), blank=False, null=False)
    year_from = models.PositiveIntegerField(verbose_name=_("year started"), blank=False, null=False)
    year_to = models.PositiveIntegerField(verbose_name=_("year ended"), blank=True, null=True)
    committee = models.BooleanField(verbose_name=_("committee"), default=True)

    class Meta:
        verbose_name = _("function")
        verbose_name_plural = _("functions")
        ordering = ['-year_from']

    def __str__(self):
        full_name = u'%s %s - %s' % (self.name, self.year_from, self.year_to or '')
        return full_name.strip()


@python_2_unicode_compatible
class Resource(models.Model):
    name = models.CharField(max_length=60, verbose_name=_("name"), blank=False, null=False)
    type = models.ForeignKey(ResourceType, related_name="resources", verbose_name=_("type"), on_delete=models.PROTECT)
    description = RedactorField(verbose_name=_("description"), blank=True, null=False)

    class Meta:
        verbose_name = _("resource")
        verbose_name_plural = _("resources")
        ordering = ('type__name', 'name')

    def __str__(self):
        return u'%s | %s' % (self.type, self.name)


@python_2_unicode_compatible
class Training(models.Model):
    member = models.ForeignKey(Contact, verbose_name=_("member"), on_delete=models.CASCADE)
    resource_type = models.ForeignKey(ResourceType, verbose_name=_("resource type"), on_delete=models.CASCADE)
    date = models.DateField(verbose_name=_("date"))

    class Meta:
        verbose_name = _("training")
        verbose_name_plural = _("trainings")
        ordering = ('member__first_name', 'resource_type__name',)

    def __str__(self):
        return u'%s - %s' % (self.resource_type, self.member)


@python_2_unicode_compatible
class Invoice(models.Model):
    INVOICE_TYPE = (
        ("E", _("expense")),
        ("I", _("invoice"))
    )
    PAYMENT_TYPE = (
        ("C", _("cash")),
        ("B", _("bank"))
    )
    date = models.DateField(verbose_name=_("date"), default=datetime.date.today)
    buyer = models.ForeignKey(Contact, verbose_name=_("buyer"), related_name="invoices", on_delete=models.PROTECT)
    seller = models.ForeignKey(Contact, verbose_name=_("seller"), related_name="expenses", on_delete=models.PROTECT)
    paid = models.DateField(verbose_name=_("date paid"), blank=True, null=True)
    payment_type = models.CharField(max_length=1, choices=PAYMENT_TYPE, default="B")
    type = models.CharField(max_length=1, choices=INVOICE_TYPE, default="I")
    draft = models.BooleanField(verbose_name=_("draft"), default=True)
    manual_total = models.FloatField(verbose_name=_("manual total"), blank=True, null=True)
    document = FilerFileField(verbose_name=_("document"), related_name="invoice_document", blank=True, null=True)

    @property
    def total(self):
        if self.manual_total:
            return self.manual_total
        else:
            # TODO change to DB aggragate once polmorphic supports aggregation
            # https://github.com/chrisglass/django_polymorphic/pull/194
            return sum([e.total for e in self.entries.all()])

    total.fget.short_description = _("total")

    def save(self, *args, **kwargs):
        if self.seller_id is None and self.type == 'I':
            self.seller = Contact.objects.filter(status__name='fablab_invoice').first()
        if self.buyer_id is None and self.type == 'E':
            self.buyer = Contact.objects.filter(status__name='fablab_invoice').first()
        super(Invoice, self).save(*args, **kwargs)

    def publish(self):
        if self.document is None:
            pdf = make_pdf('base/invoice.html', {'invoice': self})
            FileForm = modelform_factory(
                        model=filer_models.File,
                        fields=('original_filename', 'file')
                    )
            uploadform = FileForm({'original_filename': "%s.pdf" % self},
                                  {'file':  InMemoryUploadedFile(pdf, None, "%s.pdf" % self, 'pdf', pdf.tell(), None)})
            if uploadform.is_valid():
                file_obj = uploadform.save(commit=False)
                folder, created = filer_models.Folder.objects.get_or_create(name='invoices')
                file_obj.folder = folder
                file_obj.save()
                self.document = file_obj

        if self.draft:
            self.draft = False
            self.save()
            send_invoice(self)
        else:
            self.save()

    class Meta:
        verbose_name = _("invoice")
        verbose_name_plural = _("invoices")

    def __str__(self):
        return u'%s %s' % (_(dict(self.INVOICE_TYPE)[self.type]).capitalize(), self.id)


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
    user = models.ForeignKey(Contact, verbose_name=_("member"), related_name="ledger_entries", on_delete=models.PROTECT)
    invoice = models.ForeignKey(Invoice, verbose_name=_("invoice"), related_name="entries", blank=True, null=True)
    type = models.CharField(max_length=1,choices=LEDGER_TYPE,verbose_name=_("type"), default='D')

    @property
    def total(self):
        sign = 1 if self.type == 'D' else -1
        return sign * self.quantity * self.unit_price

    def __str__(self):
        return _(u"Transaction on %(date)s for %(total)s by %(user)s") % {'user': self.user, 'total':self.total, 'date': self.date}

    class Meta:
        verbose_name = _("ledger entry")
        verbose_name_plural = _("ledger entries")
        ordering = ('title', 'date',)


def current_year():
    now = datetime.datetime.now()
    return now.year


@python_2_unicode_compatible
class MembershipInvoice(LedgerEntry):
    year = models.PositiveIntegerField(verbose_name=_("year"), default=current_year)

    def is_membership_paid(self):
        if self.invoice:
            return self.invoice.paid
        return False
    is_membership_paid.short_description = _('is membership paid')

    def save(self, *args, **kwargs):
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

        super(MembershipInvoice, self).save(*args, **kwargs)

        #send membership to user
        if self.invoice.draft:
            self.invoice.publish()

    class Meta:
        verbose_name = _("membership invoice")
        verbose_name_plural = _("membership invoices")

    def __str__(self):
        return _(u"Membership %(year)s for %(user)s") % {'user': self.user, 'year': self.year}

    @classmethod
    def _validate_unique(cls, self):
        try:
            obj = cls._default_manager.get(year=self.year, user=self.user)
            if not obj == self:
                raise ValidationError(_('Membership %(year)s for %(user)s already exists!') % {'year': self.year,
                                                                                               'user': self.user})
        except cls.DoesNotExist:
            pass

    def clean(self):
        self._validate_unique(self)
        super(MembershipInvoice, self).clean()


@python_2_unicode_compatible
class Event(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("title"))
    start_date = models.DateField(verbose_name=_("start date"))
    end_date = models.DateField(verbose_name=_("end date"), blank=True, null=True)
    location = models.TextField(verbose_name=_("location"), blank=True)
    description = RedactorField(verbose_name=_("description"), blank=True)
    website = models.URLField(verbose_name=_("website"), blank=True)
    trello = models.URLField(verbose_name=_("trello"), blank=True)
    min_participants = models.PositiveIntegerField(verbose_name=_("minimum number of participants"), default=0)
    max_participants = models.PositiveIntegerField(verbose_name=_("maximum number of participants"), default=0)
    organizers = models.ManyToManyField(Contact, blank=True, null=True)

    class Meta:
        verbose_name = _("event")
        verbose_name_plural = _("events")

    def __str__(self):
        txt = u"%s (%s" % (self.title, self.start_date)
        if self.end_date:
            txt += u" - %s" % (self.end_date,)
        return txt + u")"


@python_2_unicode_compatible
class EventDocument(models.Model):
    file = FilerFileField(verbose_name=_("document"), related_name="event_document")
    event = models.ForeignKey(Event, related_name="documents", verbose_name=_("event"))

    class Meta:
        verbose_name = _("event document")
        verbose_name_plural = _("event documents")

    def __str__(self):
        return u'%s' % self.file.label


@python_2_unicode_compatible
class EventRegistration(LedgerEntry):
    event = models.ForeignKey(Event, verbose_name=_("event"), related_name="registrations", on_delete=models.PROTECT)

    class Meta:
        verbose_name = _("event registration")
        verbose_name_plural = _("event registrations")

    def save(self, *args, **kwargs):
        if not self.title or self.title is None:
            self.title = _('Event registration')

        if not self.description or self.description is None:
            self.description = str(self.event)

        super(EventRegistration, self).save(*args, **kwargs)

    def __str__(self):
        return _(u"Registration to %(event)s by %(user)s") % {'user': self.user, 'event': self.event}


@python_2_unicode_compatible
class ResourceUsage(LedgerEntry):
    resource = models.ForeignKey(Resource, verbose_name=_("resource"), related_name="usages", on_delete=models.PROTECT)
    event = models.ForeignKey(Event, verbose_name=_("event"), related_name="resource_usages", blank=True, null=True, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        if not self.title or self.title is None:
            self.title = self.resource.type.name

        super(ResourceUsage, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("resource usage")
        verbose_name_plural = _("resource usages")

    def __str__(self):
        return _(u"Usage of %(resource)s by %(user)s") % {'user': self.user, 'resource': self.resource}


@python_2_unicode_compatible
class Expense(LedgerEntry):
    event = models.ForeignKey(Event, verbose_name=_("event"), related_name="expenses", blank=True, null=True, on_delete=models.PROTECT)
    provider = models.ForeignKey(Contact, verbose_name=_("provider"), blank=True, null=True, on_delete=models.PROTECT)
    document = FilerFileField(verbose_name=_("document"), blank=True, null=True)

    class Meta:
        verbose_name = _("expense")
        verbose_name_plural = _("expenses")

    def __str__(self):
        return _(u"Expense for %(expense)s by %(user)s") % {'user': self.user, 'expense': self.title}
