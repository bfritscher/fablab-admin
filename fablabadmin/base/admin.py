import string
import random

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.forms import forms, ModelForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.safestring import mark_safe
from guardian.admin import GuardedModelAdmin, GuardedModelAdminMixin
from django.utils.translation import ugettext_lazy as _
from import_export.admin import ImportExportMixin, ExportMixin
import autocomplete_light
from django.contrib.admin import AdminSite
from tabbed_admin import TabbedModelAdmin
from django.utils.html import format_html
from django.db.models import Q
from django.core.urlresolvers import reverse
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin
from django_object_actions import BaseDjangoObjectActions, takes_instance_or_queryset, DjangoObjectActions
from .models import *
from django.template.defaultfilters import date as date_filter
from django.contrib.admin import helpers
from django.db import transaction

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
    fk_name = "member"
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
            ('yes', _('Yes')),
            ('no', _('No')),

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


class InvoicePaidListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('is invoice paid')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'ipaid'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
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
            return queryset.filter(paid__isnull=True)

        if self.value() == 'yes':
            return queryset.filter(paid__isnull=False)

class LedgerEntryMixin(object):

    def invoice_link(self, obj):
        url = reverse('admin:base_invoice_change', args=(obj.invoice.id,))
        return format_html('<a href="{}">{}</a>', url, obj.invoice)
    invoice_link.short_description = _('invoice')


    def edit_link(self, obj):
        url = reverse('admin:base_ledgerentry_change',
                      args=(obj.id,))
        return format_html(u'<a href="{}">{}</a>', url, _('Edit'))
    edit_link.short_description = _('action')


class MembershipsInline(LedgerEntryMixin, admin.TabularInline):
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


class ExpenseInline(admin.TabularInline):
    model = Expense
    extra = 1
    form = autocomplete_light.modelform_factory(Expense, fields='__all__',
                                                autocomplete_names={'provider': 'Contact', 'user': 'Contact'})


class ResourceUsageInline(admin.TabularInline):
    model = ResourceUsage
    extra = 1
    form = autocomplete_light.modelform_factory(Expense, fields='__all__',
                                                autocomplete_names={'user': 'Contact'})


class UserLedgerEntryInline(LedgerEntryMixin, admin.TabularInline):
    form = autocomplete_light.modelform_factory(LedgerEntry, fields='__all__')
    model = LedgerEntry
    extra = 0
    max_num = 0
    can_delete = False
    readonly_fields = ('date', 'title', 'description', 'quantity', 'unit_price', 'total', 'invoice',
                       'edit_link', 'invoice_link',)
    fields = (
        'date',
        'invoice_link',
        'title',
        'description',
        'quantity', 'unit_price', 'total',
        'edit_link'
    )

    def get_queryset(self, request):
        qs = super(UserLedgerEntryInline, self).get_queryset(request)
        return qs.not_instance_of(MembershipInvoice, Expense)


class UserExpenseInline(LedgerEntryMixin, admin.TabularInline):
    model = Expense
    fk_name = 'user'
    readonly_fields = ('ledgerentry_ptr', 'date', 'description', 'event', 'invoice_link', 'total', 'edit_link',)
    extra = 0
    max_num = 0
    can_delete = False
    fields = ( 'date', 'invoice_link', 'description', 'event', 'total', 'edit_link')


@admin.register(Contact)
class ContactAdmin(BaseDjangoObjectActions, ImportExportMixin, GuardedModelAdminMixin, TabbedModelAdmin):
    model = Contact
    search_fields = ('first_name', 'last_name', 'email', 'user__username', 'functions__name')
    list_display = ('full_name', 'status', 'functions','is_membership_paid_list')
    list_filter = ('status', MembershipPaidListFilter, 'functions__name')
    readonly_fields = ('is_membership_paid', 'functions', 'created', 'modified')

    change_form_template = 'base/change_form_tabbed.html'

    def get_object_actions(self, request, context, **kwargs):
        objectactions = []

        # Actions cannot be applied to new objects (i.e. Using "add" new obj)
        if 'original' in context:
            objectactions.extend(['create_invoice', 'create_expense_invoice'])
            # The obj to perform checks against to determine object actions you want to support
            obj = context['original']
            if obj and obj.status.is_member:
                m = obj.is_membership_paid()
                if m == False:
                    objectactions.extend(['create_membership', ])
            if obj and not obj.user:
                objectactions.extend(['create_user', ])

        return objectactions

    @takes_instance_or_queryset
    def create_membership(self, request, queryset):
        if request.POST.get('unit_price'):
            try:
                unit_price = request.POST.get('unit_price')
                created = []
                for c in queryset:
                    #check membership
                    if c.status.is_member:
                        m = MembershipInvoice.objects.filter(user=c, year=datetime.date.today().year).first()
                        if m is None:
                            m = MembershipInvoice.objects.create(user=c,
                                                                  year=datetime.date.today().year,
                                                                  unit_price=unit_price)
                            m.save()
                            created.append(unicode(str(c), 'utf-8'))

                self.message_user(request, _(u"created memberships for: %s") % ', '.join(created))
            except Exception as e:
                self.message_user(request, e)
            return

        return render(request, 'base/confirm_create_membership.html', {
            'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
            'queryset': queryset
        })

    create_membership.label = _("Create membership invoice")
    create_membership.short_description = _("Create membership invoice")

    def create_invoice(self, request, obj):
        invoice = invoice_open_ledegerentries(obj)
        if invoice:
            url = reverse('admin:base_invoice_change', args=(invoice.id,))
            return HttpResponseRedirect(url)

        self.message_user(request, _("Found no entries to be invoiced"))
        return

    create_invoice.label = _("create invoice")
    create_invoice.short_description = _("invoice open ledger entries")

    def create_expense_invoice(self, request, obj):
        invoice = expense_open_expenses(obj)
        if invoice:
            url = reverse('admin:base_invoice_change', args=(invoice.id,))
            return HttpResponseRedirect(url)

        self.message_user(request, _("Found no expenses to be invoiced"))
        return

    create_expense_invoice.label = _("bill expenses")
    create_expense_invoice.short_description = _("invoice open expenses")

    def create_user(self, request, obj):
        if not obj.user:
            password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))
            base_username = obj.first_name[:1].lower() + obj.last_name.lower()
            username = base_username
            i = 1
            while User.objects.filter(username=username).first():
                username = u"%s%s" % (base_username, i)
                i += 1

            obj.user = User.objects.create_user(username, obj.email, password)
            obj.save()
            self.message_user(request, _(u"Created user %(username)s with password %(password)s") % {'username': obj.user.username, 'password': password})
        return
    create_user.label = _("create user")
    create_user.short_description = _("create user account for contact")

    objectactions = ['create_membership', 'create_invoice', 'create_expense_invoice', 'create_user']
    actions = ['create_membership',]

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
                pass #html = '<input type="button" value="Create membership invoice">'
            elif m is None:
                pass #html = '<input type="button" value="send reminder" onclick="alert(\'not implemented\')">'

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

    def functions(self, obj):
        return ', '.join(obj.current_functions().values_list('name', flat=True))
    functions.short_description = _("functions")

    tab_overview = (
        (_('Contact'), {
            'fields': ('first_name',
                       'last_name',
                       'email',
                       'phone',
                       'status',
                       'is_membership_paid',
                       'comment',
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
                           ('created',
                           'modified'),
                           'birth_year',
                         'education',
                         'profession',
                         'employer',
                         'interests')
            }),
    )
    tabs = [
        (_('Overview'), tab_overview),
        (_('Detail'), tab_about),
        (_('Trainings'), tab_trainings),
        (_('Functions'), tab_functions),
        (_('Memberships'), (MembershipsInline,)),
        (_('Ledger entries'), (UserLedgerEntryInline,)),
        (_('Expenses'), (UserExpenseInline,))
    ]

    class Media:
        css = { "all" : ("css/hide_admin_original.css",) }

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Resource)
class ResourceAdmin(ImportExportMixin, GuardedModelAdmin):
    list_filter = ('type__name',)
    ordering = ('type__name', 'name',)
    inlines = (ResourceUsageInline,)
    readonly_fields = ('slug',)
    fields = (('name', 'slug'),
              'type',
              ('price', 'price_unit'),
              'image',
              'description',
              )


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
        ('type', 'quantity', 'unit_price', 'total')
    )


@admin.register(Invoice)
class InvoiceAdmin(ExportMixin, GuardedModelAdminMixin, BaseDjangoObjectActions, admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(Invoice, fields='__all__',
                                                autocomplete_names={'seller': 'Contact',
                                                                    'buyer': 'Contact'})
    search_fields = ('id', 'seller__first_name', 'seller__last_name', 'buyer__first_name', 'buyer__last_name')
    list_display = ('id', '__str__', 'buyer', 'seller', 'payment_type', 'total', 'paid', 'draft', )
    list_display_links = ('id', '__str__')
    list_filter = (InvoicePaidListFilter, 'type', 'payment_type', 'draft')
    date_hierarchy = "date"
    inlines = (LedgerEntryInline, )
    fields = (
        ('date', 'draft'),
         'buyer', 'seller',
         ('payment_type', 'paid'),
         'manual_total', 'document', 'type'
    )
    change_form_template = 'base/change_form.html'

    def preview(self, request, obj):
        return HttpResponseRedirect('/admin/invoice/%s' % obj.id)

    preview.label = _('preview')
    preview.short_description = _('preview of the invoice')
    preview.attrs = {
        'target': '_blank',
    }

    def publish(self, request, obj):
        obj.publish()
        self.message_user(request, _(u'invoice sent to %s') % obj.buyer.email)
        return

    publish.label = _('publish')
    publish.short_description = _('publish invoice and send it by email')

    def get_object_actions(self, request, context, **kwargs):
        objectactions = []

        # Actions cannot be applied to new objects (i.e. Using "add" new obj)
        if 'original' in context:
            # The obj to perform checks against to determine object actions you want to support
            obj = context['original']
            if obj and obj.draft:
                objectactions.extend(['preview', 'publish'])

        return objectactions

    objectactions = ('preview', 'publish')


class LedgerEntryChildAdmin(GuardedModelAdminMixin, PolymorphicChildModelAdmin):
    base_model = LedgerEntry
    form = autocomplete_light.modelform_factory(LedgerEntry, fields='__all__',
                                                 autocomplete_names={'user': 'Contact', 'provider': 'Contact'})
    # # By using these `base_...` attributes instead of the regular ModelAdmin `form` and `fieldsets`,
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
    form = autocomplete_light.modelform_factory(Expense, fields='__all__',
                                                autocomplete_names={'user': 'Contact'})

    def get_form(self, request, obj=None, **kwargs):
        # Proper kwargs are form, fields, exclude, formfield_callback
        if obj: # obj is not N  one, so this is a change page
            pass
            #kwargs['exclude'] = ['foo', 'bar',]
        else: # obj is None, so this is an add page
            kwargs['fields'] = ('date', 'user', 'resource', 'description', 'quantity', 'unit_price', 'event')

        form = super(ResourceUsageAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['description'].initial = "%s: " % date_filter(datetime.date.today(), 'SHORT_DATE_FORMAT')
        return form


class EventRegistrationAdmin(LedgerEntryChildAdmin):
    base_model = EventRegistration
    form = autocomplete_light.modelform_factory(EventRegistration, fields='__all__',
                                                autocomplete_names={'user': 'Contact'})

    def get_form(self, request, obj=None, **kwargs):
        # Proper kwargs are form, fields, exclude, formfield_callback
        if obj: # obj is not N  one, so this is a change page
            pass
            #kwargs['exclude'] = ['foo', 'bar',]
        else: # obj is None, so this is an add page
            kwargs['fields'] = ('date', 'user', 'event', 'quantity', 'unit_price')

        return super(EventRegistrationAdmin, self).get_form(request, obj, **kwargs)


class ExpenseAdmin(LedgerEntryChildAdmin):
    base_model = Expense
    form = autocomplete_light.modelform_factory(Expense, fields='__all__',
                                                autocomplete_names={'provider': 'Contact', 'user': 'Contact'})

    def get_form(self, request, obj=None, **kwargs):
        # Proper kwargs are form, fields, exclude, formfield_callback
        if obj: # obj is not N  one, so this is a change page
            kwargs['fields'] = (
                'date',
                'user',
                'title',
                'description',
                'quantity', 'unit_price',
                'event',
                'provider',
                'document',
                'invoice'
            )
        else: # obj is None, so this is an add page
            kwargs['fields'] = (
                'date',
                'user',
                'title',
                'description',
                'quantity', 'unit_price',
                'event',
                'provider',
                'document',
            )

        return super(ExpenseAdmin, self).get_form(request, obj, **kwargs)


@admin.register(LedgerEntry)
class LedgerEntryAdmin(ExportMixin, GuardedModelAdminMixin, PolymorphicParentModelAdmin):
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
    ordering = ('-date',)
    list_display = ('__str__', 'title', 'description', 'user')
    list_filter = (
        ('user', admin.RelatedOnlyFieldListFilter),
    )


class EventDocumentInline(admin.StackedInline):
    model = EventDocument
    extra = 1


class EventRegistrationInline(admin.TabularInline):
    model = EventRegistration
    extra = 1
    form = autocomplete_light.modelform_factory(EventRegistration, fields='__all__',
                                                autocomplete_names={'user': 'Contact'})
    readonly_fields = ('date', 'total')
    fields = ('date', 'user', 'quantity', 'unit_price', 'total')


@admin.register(Event)
class EventAdmin(ImportExportMixin, GuardedModelAdminMixin, TabbedModelAdmin):
    model = Event
    filter_horizontal = ('organizers',)
    search_fields = ('title',)
    date_hierarchy = "start_date"
    readonly_fields = ('slug',)

    change_form_template = 'base/change_form_tabbed.html'

    tab_overview = (
        (_('Event'), {
            'fields': (('title','slug'),
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
    tab_expenses = (ExpenseInline,)
    tab_resource_usages = (ResourceUsageInline,)

    tabs = [
        (_('Overview'), tab_overview),
        (_('Documents'), tab_documents),
        (_('Registrations'), tab_registrations),
        (_('Expenses'), tab_expenses),
        (_('Resource usages'), tab_resource_usages)
    ]
