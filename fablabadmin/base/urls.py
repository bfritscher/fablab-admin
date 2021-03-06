from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'lang', views.change_lang),
    url(r'admin/invoice/(\d+)', views.invoice),
    url(r'admin/invoice_html/(\d+)', views.invoice_html),
    url(r'admin/mail_template/(\d+)', views.mail_template),
    url(r'^$',  views.index, name='index'),
    url(r'register/success',  views.register_success, name='register_success'),
    url(r'register',  views.register, name='register'),
    url(r'resource/(?P<id>\d+)',  views.resource, name='resource'),
    url(r'resource/(?P<slug>.+)',  views.resource, name='resource'),
    url(r'dokuwiki_login', views.dokuwiki_login),
    url(r'rest_login', views.user_login)
]