from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'consolidation', views.consolidation, name="consolidation"),
    url(r'ccvshop_order_webhook', views.ccvshop_order_webhook, name="ccvshop_order_webhook"),
]