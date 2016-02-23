from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'profile/edit', views.profile_edit, name="profile_edit"),
    url(r'profile', views.profile, name="profile"),
]