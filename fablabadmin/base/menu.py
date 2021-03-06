"""
This file was generated with the custommenu management command, it contains
the classes for the admin menu, you can customize this class as you want.

To activate your custom menu add the following to your settings.py::
    ADMIN_TOOLS_MENU = 'app.menu.CustomMenu'
"""

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from admin_tools.menu import items, Menu


class CustomMenu(Menu):
    """
    Custom Menu for app admin site.
    """
    def __init__(self, **kwargs):
        Menu.__init__(self, **kwargs)

        app_menu = items.AppList(
                _('Applications'),
                exclude=('django.contrib.*',
                     'fablabadmin.base.models.ContactStatus',
                     'fablabadmin.base.models.ResourceType',
                     'fablabadmin.accounting.models.BankTransaction',
                     'filer*')
            )
        admin_menu = items.AppList(
                _('Administration'),
                models=('django.contrib.*',
                    'fablabadmin.base.models.ContactStatus',
                    'fablabadmin.base.models.ResourceType',
                    'fablabadmin.accounting.models.BankTransaction',
                    'filer*')
            )
        app_menu.children += [items.MenuItem(_('Accounting'), children=[
            items.MenuItem(_('Consolidation'), '/admin/accounting/consolidation')
        ])]

        self.children += [
            items.MenuItem(_('Dashboard'), reverse('admin:index')),
            items.Bookmarks(),
            app_menu,
            admin_menu,
            items.MenuItem(_('report bug / new feature'), 'https://github.com/bfritscher/fablab-admin/issues')

        ]

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        return super(CustomMenu, self).init_with_context(context)
