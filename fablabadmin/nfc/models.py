from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from fablabadmin.base.models import Contact


@python_2_unicode_compatible
class Token(models.Model):
    id = models.CharField(verbose_name=_('token'), max_length=20, primary_key=True,
                          blank=False, null=False)
    owner = models.ForeignKey(Contact, related_name="tokens", verbose_name=_("owner"),
                              on_delete=models.PROTECT, blank=True, null=True)
    description = models.CharField(verbose_name=_('description'), max_length=50,
                                   blank=True, null=False)
    modified_date = models.DateTimeField(verbose_name=_("modified"), auto_now=True)

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return u'%s (%s)' % (self.id, self.owner)


@python_2_unicode_compatible
class LogEntry(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("timestamp"))
    token = models.ForeignKey(Token, related_name="logentries", verbose_name=_("token"),
                              on_delete=models.PROTECT)
    owner = models.ForeignKey(Contact, related_name="logentries", verbose_name=_("owner"),
                              on_delete=models.PROTECT,
                              blank=True, null=True)
    payload = models.TextField(verbose_name=_("payload"), blank=True)

    class Meta:
        verbose_name = _("log entry")
        verbose_name_plural = _("log entries")
        ordering = ('-timestamp',)

    def __str__(self):
        return u'%s %s %s' % (self.timestamp, self.token.id,  self.owner)

