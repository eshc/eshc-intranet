"""eshcIntranet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include
from django.contrib import admin
from allauth.account import urls
from django.urls import path

import home

urlpatterns = [
    path('', include('home.urls')),
    path('admin/', admin.site.urls),
    # url(r'^users/', include('users.urls', namespace='users')),
    path('leases/', include('leases.urls')),
    path('polls/', include('polls.urls')),
    path('hours/', include('hours.urls')),
    path('whiteboard/', include('whiteboard.urls')),
    path('apply/', include('apply.urls')),
    path('finance/', include('finance.urls')),

    # allauth
    path('accounts/', include('allauth.urls')),
    path('accounts/profile/', home.views.profile, name='profile'),

    path('notifications/', include('django_nyt.urls')),
    path('wiki/', include('wiki.urls')),
]

