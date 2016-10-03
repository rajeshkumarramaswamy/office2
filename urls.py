"""shop URL Configuration

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
from django.conf.urls import include, url
from django.contrib import admin
from customer_data.views import *


urlpatterns = [
    url(r'^$', 'customer_data.views.index', name='home'),
    url(r'^dashboard/', 'customer_data.views.layout', name='layout'),
    url(r'^display/$', 'customer_data.views.display', name='display'),
    url(r'^savefilter/$', 'customer_data.views.savefilter', name='savefilter'),
    url(r'^filtername=.*/', 'customer_data.views.index', name='loadfilter'),
    url(r'^react/$', 'customer_data.views.react', name='react'),
    url(r'^admin/', include(admin.site.urls)),
]
