from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.forms import forms, ModelForm
from guardian.admin import GuardedModelAdmin
from django.utils.translation import ugettext_lazy as _
from import_export.admin import ImportExportMixin


from .models import *


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


@admin.register(ContactStatus)
class ContactStatusAdmin(GuardedModelAdmin):
    pass


@admin.register(Contact)
class ContactAdmin(ImportExportMixin, GuardedModelAdmin):
    inlines = (FunctionInline,)
    class Media:
        css = { "all" : ("css/hide_admin_original.css",) }

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)