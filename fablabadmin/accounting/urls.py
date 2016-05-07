from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'consolidation', views.consolidation, name="consolidation"),
]