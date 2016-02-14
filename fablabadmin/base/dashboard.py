"""
This file was generated with the customdashboard management command, it
contains the two classes for the main dashboard and app index dashboard.
You can customize these classes as you want.

To activate your index dashboard add the following to your settings.py::
    ADMIN_TOOLS_INDEX_DASHBOARD = 'app.dashboard.CustomIndexDashboard'

And to activate the app index dashboard::
    ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'app.dashboard.CustomAppIndexDashboard'
"""
import datetime

from admin_tools.dashboard.modules import DashboardModule
from django.db.models import Q
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from fablabadmin.base.models import Function

from admin_tools.dashboard import modules, Dashboard, AppIndexDashboard
from admin_tools.utils import get_admin_site_name


class RecentActions(DashboardModule):
    """
    Module that lists the recent actions for the current user.
    As well as the :class:`~admin_tools.dashboard.modules.DashboardModule`
    properties, the :class:`~admin_tools.dashboard.modules.RecentActions`
    takes three extra keyword arguments:

    ``include_list``
        A list of contenttypes (e.g. "auth.group" or "sites.site") to include,
        only recent actions that match the given contenttypes will be
        displayed.

    ``exclude_list``
        A list of contenttypes (e.g. "auth.group" or "sites.site") to exclude,
        recent actions that match the given contenttypes will not be
        displayed.

    ``limit``
        The maximum number of children to display. Default value: 10.

    Here's a small example of building a recent actions module::

        from admin_tools.dashboard import modules, Dashboard

        class MyDashboard(Dashboard):
            def __init__(self, **kwargs):
                Dashboard.__init__(self, **kwargs)

                # will only list the django.contrib apps
                self.children.append(modules.RecentActions(
                    title='Django CMS recent actions',
                    include_list=('cms.page', 'cms.cmsplugin',)
                ))

    The screenshot of what this code produces:

    .. image:: images/recentactions_dashboard_module.png
    """
    title = _('Recent Actions')
    template = 'dashboard/modules/recent_actions.html'
    limit = 10
    include_list = None
    exclude_list = None

    def __init__(self, title=None, limit=10, include_list=None,
                 exclude_list=None, **kwargs):
        self.include_list = include_list or []
        self.exclude_list = exclude_list or []
        kwargs.update({'limit': limit})
        super(RecentActions, self).__init__(title, **kwargs)

    def init_with_context(self, context):
        if self._initialized:
            return
        from django.db.models import Q
        from django.contrib.admin.models import LogEntry

        request = context['request']

        def get_qset(list):
            # Import this here to silence RemovedInDjango19Warning. See #15
            from django.contrib.contenttypes.models import ContentType

            qset = None
            for contenttype in list:
                if isinstance(contenttype, ContentType):
                    current_qset = Q(content_type__id=contenttype.id)
                else:
                    try:
                        app_label, model = contenttype.split('.')
                    except:
                        raise ValueError(
                            'Invalid contenttype: "%s"' % contenttype
                        )
                    current_qset = Q(
                        content_type__app_label=app_label,
                        content_type__model=model
                    )
                if qset is None:
                    qset = current_qset
                else:
                    qset = qset | current_qset
            return qset

        qs = LogEntry.objects.all()

        if self.include_list:
            qs = qs.filter(get_qset(self.include_list))
        if self.exclude_list:
            qs = qs.exclude(get_qset(self.exclude_list))

        self.children = qs.select_related('content_type', 'user')[:self.limit]
        if not len(self.children):
            self.pre_content = _('No recent actions.')
        self._initialized = True


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for app.
    """
    def init_with_context(self, context):
        site_name = get_admin_site_name(context)
        # append a link list module for "quick links"
        # self.children.append(modules.LinkList(
        #     _('Quick links'),
        #     layout='inline',
        #     draggable=False,
        #     deletable=False,
        #     collapsible=False,
        #     children=[
        #         [_('Return to site'), '/'],
        #         [_('Change password'),
        #          reverse('%s:password_change' % site_name)],
        #         [_('Log out'), reverse('%s:logout' % site_name)],
        #     ]
        # ))

        # append an app list module for "Applications"
        self.children.append(modules.AppList(
            _('Applications'),
            exclude=('django.contrib.*',
                     'fablabadmin.base.models.ContactStatus',
                     'fablabadmin.base.models.ResourceType',
                     'filer*'),
        ))

        # append an app list module for "Administration"
        self.children.append(modules.AppList(
            _('Administration'),
            models=('django.contrib.*',
                    'fablabadmin.base.models.ContactStatus',
                    'fablabadmin.base.models.ResourceType',
                    'filer*'),
        ))

        current_committee = Function.objects.filter(
            Q(year_from__lte=datetime.date.today().year),
            Q(committee=True),
            Q(year_to__gte=datetime.date.today().year) | Q(year_to__isnull=True)).all()

        html = "\n".join(["<tr><td>%s</td><td>%s</td></tr>" % (f.name, f.member) for f in current_committee])

        self.children.append(modules.DashboardModule(
            _('Committee'),
            pre_content=format_html('<table class="comittee"><tr><th>%s</th><th>%s</th></tr>%s</table>' % (_('Function'), _('Member'), html))
        ))

        # append a recent actions module
        self.children.append(RecentActions(_('Recent Actions'), 20))

        # append another link list module for "support".
        # self.children.append(modules.LinkList(
        #     _('Support'),
        #     children=[
        #         {
        #             'title': _('Django documentation'),
        #             'url': 'http://docs.djangoproject.com/',
        #             'external': True,
        #         },
        #         {
        #             'title': _('Django "django-users" mailing list'),
        #             'url': 'http://groups.google.com/group/django-users',
        #             'external': True,
        #         },
        #         {
        #             'title': _('Django irc channel'),
        #             'url': 'irc://irc.freenode.net/django',
        #             'external': True,
        #         },
        #     ]
        # ))


class CustomAppIndexDashboard(AppIndexDashboard):
    """
    Custom app index dashboard for app.
    """

    # we disable title because its redundant with the model list module
    title = ''

    def __init__(self, *args, **kwargs):
        AppIndexDashboard.__init__(self, *args, **kwargs)


        # append a model list module and a recent actions module
        self.children += [
            modules.ModelList(self.app_title, self.models,
                               exclude=('django.contrib.*',
                     'fablabadmin.base.models.ContactStatus',
                     'fablabadmin.base.models.ResourceType',
                     'filer*')),
            RecentActions(
                _('Recent Actions'),
                include_list=self.get_app_content_types(),
                limit=20
            )
        ]

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        return super(CustomAppIndexDashboard, self).init_with_context(context)
