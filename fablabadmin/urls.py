"""fablabadmin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
import settings
from django.conf.urls import include, url
from django.contrib import admin

from rest_framework import routers

import fablabadmin.nfc.views as nfc
from fablabadmin.base import urls
from django.contrib.auth.views import password_change

import autocomplete_light.shortcuts as al
from fablabadmin.base.autocomplete_light_registry import *
al.autodiscover()
admin.autodiscover()

router = routers.DefaultRouter(trailing_slash=False)


#router.register(r'games', views.GameViewSet)
#router.register(r'departments', views.DepartmentViewSet)
#router.register(r'languages', views.LanguageViewSet)
#router.register(r'questions', views.QuestionViewSet)

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^autocomplete/', include('autocomplete_light.urls')),
    url(r'^redactor/', include('redactor.urls')),
    url(r'^api/nfc/record', nfc.record_log_entry),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^filer/', include('filer.urls')),
    url('^accounts/password_change/', password_change, {'template_name': 'accounts/password_change_form.html'}),
    url('^accounts/', include('django.contrib.auth.urls')),
    url('^accounts/', include('fablabadmin.accounts.urls')),
    url(r'^', include(urls))
]
