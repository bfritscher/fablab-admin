from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.forms import forms, ModelForm
from django.utils.safestring import mark_safe
from guardian.admin import GuardedModelAdmin
from django.utils.translation import ugettext_lazy as _
from import_export.admin import ImportExportMixin
import autocomplete_light
from django.contrib.admin import AdminSite
from tabbed_admin import TabbedModelAdmin
from django.utils.html import format_html
from django.db.models import Q
from django.core.urlresolvers import reverse
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin

from .models import *

AdminSite.site_title = 'FabLab - admin'
AdminSite.index_title = 'Dashboard'


@admin.register(ContactStatus)
class ContactStatusAdmin(GuardedModelAdmin):
    pass


@admin.register(ResourceType)
class ResourceTypeAdmin(GuardedModelAdmin):
   pass


class ContactInline(admin.StackedInline):
    model = Contact
    can_delete = False
    verbose_name_plural = "contacts"


class UserAdmin(BaseUserAdmin):
    def c(field):
        f = lambda obj: getattr(obj.contact, field)
        f.short_description = _(field.replace('_', ' '))
        return f

    list_display = (c('first_name'), c('last_name'))
    inlines = (ContactInline,)


class FunctionAdminForm(ModelForm):
    def clean(self):
        year_from = self.cleaned_data.get("year_from")
        year_to = self.cleaned_data.get("year_to")
        if year_from and year_to and year_from > year_to:
            raise forms.ValidationError(_("Start year cannot be greater than end year."))
        return self.cleaned_data


class FunctionInline(admin.TabularInline):
    model = Function
    form = FunctionAdminForm
    extra = 1


class TrainingInline(admin.TabularInline):
    model = Training
    extra = 1


class MembershipPaidListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('is membership paid')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'mpaid'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('no', _('no')),
            ('yes', _('yes')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == 'no':
            ids = MembershipInvoice.objects.filter(year=datetime.date.today().year, invoice__paid__isnull=True).values_list('id', flat=True)
            return queryset.filter(ledger_entries__id__in=ids)

        if self.value() == 'yes':
            ids = MembershipInvoice.objects.filter(year=datetime.date.today().year, invoice__paid__isnull=False).values_list('id', flat=True)
            return queryset.filter(ledger_entries__id__in=ids)


class MembershipsInline(admin.TabularInline):
    model = MembershipInvoice
    readonly_fields = ('ledgerentry_ptr', 'year', 'invoice_link', 'total', 'is_membership_paid',)
    extra = 0
    max_num = 0
    can_delete = False
    fields = ('year', 'invoice_link', 'total', 'is_membership_paid')

    def is_membership_paid(self, obj):
        answer_class = 'no'
        answer_text = _('no')
        if obj.is_membership_paid():
            answer_class = 'yes'
            answer_text = _('yes')
        return format_html('<span class="membership-{}">{}</span>', answer_class, answer_text)

    def invoice_link(self, obj):
        url = reverse('admin:base_invoice_change', args=(obj.invoice.id,))
        return format_html('<a href="{}">{}</a>', url, obj.invoice)
    invoice_link.short_description = _('invoice')


@admin.register(Contact)
class ContactAdmin(ImportExportMixin, TabbedModelAdmin):
    model = Contact
    search_fields = ('first_name', 'last_name', 'email', 'user__username')
    list_display = ('full_name', 'status', 'is_membership_paid_list')
    list_filter = ('status', MembershipPaidListFilter)
    readonly_fields = ('is_membership_paid',)

    def is_membership_paid(self, obj):
        if obj.status.is_member:
            answer_class = 'no'
            answer_text = _('no')
            html = ''
            m = obj.is_membership_paid()
            if m:
                answer_class = 'yes'
                answer_text = _('yes')
            elif m == False:
                html = '<input type="button" value="Create membership invoice">'
            elif m is None:
                html = '<input type="button" value="send reminder" onclick="alert(\'not implemented\')">'

            return format_html('<span class="membership-{}">{}</span> {}', answer_class, answer_text, mark_safe(html))
        return _('-')
    is_membership_paid.short_description = _('is %(year)s membership paid') % {'year': datetime.date.today().year}

    def is_membership_paid_list(self, obj):
        if obj.status.is_member:
            answer_class = 'no'
            answer_text = _('no')
            m = obj.is_membership_paid()
            if m:
                answer_class = 'yes'
                answer_text = _('yes')
            return format_html('<span class="membership-{}">{}</span>', answer_class, answer_text)
        return _('-')
    is_membership_paid_list.short_description = is_membership_paid.short_description

    tab_overview = (
        (_('Contact'), {
            'fields': ('first_name',
                       'last_name',
                       'email',
                       'phone',
                       'status',
                       'is_membership_paid',
                      )
        }),
        (_('Address'), {
            'fields': ('address',
                       'postal_code',
                       'city',
                       'country'
                       )
        }),
        (_('Payment'), {
            'fields': ('payment_info',),
        })
    )
    tab_trainings = (TrainingInline,)
    tab_functions = (FunctionInline,)
    tab_about = (
            (None, {
                'fields': ('user',
                           'birth_year',
                         'education',
                         'profession',
                         'employer',
                         'interests')
            }),
    )
    tabs = [
        (_('Overview'), tab_overview),
        (_('Trainings'), tab_trainings),
        (_('Functions'), tab_functions),
        (_('Detail'), tab_about),
        (_('Memberships'), (MembershipsInline,))
    ]
    class Media:
        css = { "all" : ("css/hide_admin_original.css",) }

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Resource)
class ResourceAdmin(GuardedModelAdmin):
    list_filter = ('type__name',)
    ordering = ('type__name', 'name',)


class LedgerEntryInline(admin.StackedInline):
    form = autocomplete_light.modelform_factory(LedgerEntry, fields='__all__')
    model = LedgerEntry
    extra = 1
    readonly_fields = ('total',)
    fields = (
        'date',
        'title',
        'description',
        'user',
        ('quantity', 'unit_price', 'total')
    )


@admin.register(Invoice)
class InvoiceAdmin(GuardedModelAdmin):
    form = autocomplete_light.modelform_factory(Invoice, fields='__all__',
                                                autocomplete_names={'seller': 'Contact',
                                                                    'buyer': 'Contact'})
    search_fields = ('id', 'seller__first_name', 'seller__last_name', 'buyer__first_name', 'buyer__last_name')
    list_display = ('id', '__str__', 'buyer', 'seller', 'total', 'paid',)
    list_filter = ('paid', 'type', 'payment_type', 'draft')
    #readonly_fields = ('is_membership_paid',)
    date_hierarchy = "date"
    inlines = (LedgerEntryInline, )
    fields = (
        ('date', 'draft'),
         'buyer', 'seller',
         ('payment_type', 'paid'),
         'manual_total', 'document', 'type'
    )


class LedgerEntryChildAdmin(PolymorphicChildModelAdmin, GuardedModelAdmin):
    base_model = LedgerEntry
    form = autocomplete_light.modelform_factory(MembershipInvoice, fields='__all__',
                                                autocomplete_names={'user': 'Contact'})
    # By using these `base_...` attributes instead of the regular ModelAdmin `form` and `fieldsets`,
    # the additional fields of the child models are automatically added to the admin form.
    #base_form = ...
    #base_fieldsets = (
    #    ...
    #)


class MembershipInvoiceAdmin(LedgerEntryChildAdmin):
    base_model = MembershipInvoice
    form = autocomplete_light.modelform_factory(MembershipInvoice, fields='__all__',
                                                autocomplete_names={'user': 'Member'})

    def get_form(self, request, obj=None, **kwargs):
            # Proper kwargs are form, fields, exclude, formfield_callback
            if obj: # obj is not N  one, so this is a change page
                pass
                #kwargs['exclude'] = ['foo', 'bar',]
            else: # obj is None, so this is an add page
                kwargs['fields'] = ('date', 'user', 'year', 'unit_price')

            return super(MembershipInvoiceAdmin, self).get_form(request, obj, **kwargs)


class ResourceUsageAdmin(LedgerEntryChildAdmin):
    base_model = ResourceUsage


class EventRegistrationAdmin(LedgerEntryChildAdmin):
    base_model = EventRegistration


class ExpenseAdmin(LedgerEntryChildAdmin):
    base_model = Expense


@admin.register(LedgerEntry)
class LedgerEntryAdmin(PolymorphicParentModelAdmin, GuardedModelAdmin):
    """ The parent model admin """
    base_model = LedgerEntry
    child_models = (
        (MembershipInvoice, MembershipInvoiceAdmin),
        (ResourceUsage, ResourceUsageAdmin),
        (EventRegistration, EventRegistrationAdmin),
        (Expense, ExpenseAdmin),
        (LedgerEntry, LedgerEntryChildAdmin)
    )
    date_hierarchy = "date"


class EventDocumentInline(admin.StackedInline):
    model = EventDocument
    extra = 1


class EventRegistrationInline(admin.TabularInline):
    model = EventRegistration
    extra = 1
    form = autocomplete_light.modelform_factory(MembershipInvoice, fields='__all__',
                                                autocomplete_names={'user': 'Contact'})


@admin.register(Event)
class EventAdmin(TabbedModelAdmin, GuardedModelAdmin):
    filter_horizontal = ('organizers',)
    search_fields = ('title',)
    date_hierarchy = "start_date"
    #list_display = ('full_name', 'status')

    tab_overview = (
        (_('Event'), {
            'fields': ('title',
                       'start_date',
                       'end_date',
                       'website',
                       'trello',
                       'description',
                       )
        }),
        (_('Detail'), {
            'fields': ('location',
                       'min_participants',
                       'max_participants',
                       'organizers'
                       )
        }),
    )

    tab_documents = (EventDocumentInline,)
    tab_registrations = (EventRegistrationInline,)

    tabs = [
        (_('Overview'), tab_overview),
        (_('Documents'), tab_documents),
        (_('Registrations'), tab_registrations),
    ]
