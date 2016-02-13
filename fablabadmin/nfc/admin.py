from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import ModelAdmin
from django.core.urlresolvers import reverse
from django.utils.html import format_html

from fablabadmin.nfc.models import Token, LogEntry
from django.contrib import admin
import autocomplete_light


@admin.register(Token)
class TokenAdmin(ModelAdmin):
    search_fields = ['owner__first_name', 'owner__last_name', 'id']
    list_display = ('id', 'owner', 'modified_date')
    form = autocomplete_light.modelform_factory(Token, fields='__all__',
                                                autocomplete_names={'owner': 'Contact'})


@admin.register(LogEntry)
class LogEntryAdmin(ModelAdmin):
    actions = None
    search_fields = ['owner__first_name', 'owner__last_name', 'token__id']
    date_hierarchy = "timestamp"
    list_display = ['timestamp', 'token_link', 'owner_link']
    list_filter = (
        ('owner', admin.RelatedOnlyFieldListFilter),
    )
    readonly_fields = ['token', 'owner', 'payload']

    def token_link(self, obj):
        url = reverse('admin:nfc_token_change', args=(obj.token.id,))
        return format_html('<a href="{}">{}</a>', url, obj.token.id)
    token_link.short_description = _('token')

    def owner_link(self, obj):
        if obj.owner:
            url = reverse('admin:base_contact_change', args=(obj.owner.id,))
            return format_html('<a href="{}">{}</a>', url, obj.owner)
        else:
            return "-"
    owner_link.short_description = _('owner')
