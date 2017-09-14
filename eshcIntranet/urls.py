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
from django.conf.urls import url, include
from django.contrib import admin
from allauth.account import urls
from machina.app import board
import home

urlpatterns = [
	url(r'', include('home.urls', namespace='home')),
    url(r'^admin/', admin.site.urls),
    # url(r'^users/', include('users.urls', namespace='users')),
    url(r'^leases/', include('leases.urls', namespace='leases')),
    url(r'^polls/', include('polls.urls', namespace='polls')),
    url(r'^hours/', include('hours.urls', namespace='hours')),
    url(r'^whiteboard/', include('whiteboard.urls', namespace='whiteboard')),

    # Waliki
    # url(r'^wiki/', include('waliki.urls')),

    # allauth
    url(r'^accounts/', include('allauth.urls')),
    url(r'^accounts/profile/', home.views.profile, name='profile'),

    # Machina
    url(r'^forum/', include(board.urls)),
]

from wiki.urls import get_pattern as get_wiki_pattern
from django_nyt.urls import get_pattern as get_nyt_pattern
urlpatterns += [
    url(r'^notifications/', get_nyt_pattern()),
    url(r'wiki/', get_wiki_pattern())
]
