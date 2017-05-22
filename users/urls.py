"""Defines URL patters for users"""

from django.conf.urls import url, include
from django.contrib.auth.views import login

from . import views

urlpatterns = [
	# Login page
	url(r'^login/$', login, {'template_name': 'users/login.html'}, name='login'),
	# url('^', include('django.contrib.auth.urls')),
]
