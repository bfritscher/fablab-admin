from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from redactor.fields import RedactorField


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
        return '%s | %s' % (self.type, self.name);


class Training(models.Model):
    member = models.ForeignKey(Contact, verbose_name=_("member"), on_delete=models.CASCADE)
    resource = models.ForeignKey(ResourceType, verbose_name=_("resource"), on_delete=models.CASCADE)
    date = models.DateField(verbose_name=_("date"))

    def __str__(self):
        return '%s - %s' % (self.resource, self.member);


# class Invoice:
#     date
#     buyer:contact
#     seller:contact
#     paid = date
#     payment_type cash post
#     invoice or payment
#     document
#
#
# class LedgerEntry:
#     date
#     title
#     description
#     quantity
#     unit_price
#     user
#     type D/C
#     invoice?
#     //virtual total
#
# class MembershipInvoice(LedgerEntry):
#    year
#    #auto create invoice
#
#
#
# class ResourceUsage(LedgerEntry):
#     resource
#
#
#
# class Event:
#     title
#     date_start
#     date_end
#     description
#     nb_participants
#     has_many organizers
#
# class EventRegistration(LedgerEntry):
#     event
#    #create invoice
#
#
# class Expense(LedgerEntry):
#     event
#     picture
