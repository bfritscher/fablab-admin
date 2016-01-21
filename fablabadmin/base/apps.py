from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class BaseConfig(AppConfig):
    name = 'fablabadmin.base'
    verbose_name = _("Fablab Admin Base")