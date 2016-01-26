from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.forms import forms, ModelForm
from guardian.admin import GuardedModelAdmin
from django.utils.translation import ugettext_lazy as _
from import_export.admin import ImportExportMixin
import autocomplete_light
from django.contrib.admin import AdminSite
from tabbed_admin import TabbedModelAdmin

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


class FunctionInline(admin.TabularInline):
    model = Function
    extra = 1

class TrainingInline(admin.TabularInline):
    model = Training
    extra = 1

@admin.register(Contact)
class ContactAdmin(ImportExportMixin, TabbedModelAdmin):
    model = Contact
    search_fields = ('first_name' , 'last_name', 'email', 'user__username')
    list_display = ('full_name', 'status')
    list_filter = ('status',)
    #inlines = (FunctionInline,)
    tab_overview = (
        (_('Contact'), {
            'fields': ('first_name',
                       'last_name',
                       'email',
                       'phone',
                       'status',
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
        (_('Detail'), tab_about)
    ]
    class Media:
        css = { "all" : ("css/hide_admin_original.css",) }

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class FunctionAdminForm(ModelForm):
    def clean(self):
        year_from = self.cleaned_data.get("year_from")
        year_to = self.cleaned_data.get("year_to")
        if year_from and year_to and year_from > year_to:
            raise forms.ValidationError(_("Start year cannot be greater than end year."))
        return self.cleaned_data


@admin.register(Function)
class FunctionAdmin(GuardedModelAdmin):
    form = FunctionAdminForm


@admin.register(Resource)
class ResourceAdmin(GuardedModelAdmin):
    pass


@admin.register(Training)
class TrainingAdmin(GuardedModelAdmin):
    form = autocomplete_light.modelform_factory(Training, fields='__all__')


@admin.register(Invoice)
class InvoiceAdmin(GuardedModelAdmin):
    pass


@admin.register(LedgerEntry)
class LedgerEntryAdmin(GuardedModelAdmin):
    pass


@admin.register(MembershipInvoice)
class MembershipInvoiceAdmin(GuardedModelAdmin):
    pass


@admin.register(ResourceUsage)
class ResourceUsageAdmin(GuardedModelAdmin):
    pass


@admin.register(Event)
class EventAdmin(GuardedModelAdmin):
    pass


@admin.register(EventRegistration)
class EventRegistrationAdmin(GuardedModelAdmin):
    pass


@admin.register(Expense)
class ExpenseAdmin(GuardedModelAdmin):
    pass


