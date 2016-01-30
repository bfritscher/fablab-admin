from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'lang', views.change_lang),
    url(r'invoice/(\d)', views.invoice),
    url(r'invoice_html/(\d)', views.invoice_html),
    url(r'mail_template/(\d)', views.mail_template)
]