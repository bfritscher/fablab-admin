from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'lang', views.change_lang),
    url(r'invoice/(\d)', views.invoice)
]