"""Defines URL patters for users"""

from django.conf.urls import url, include
from django.contrib.auth.views import login

from . import views

urlpatterns = [
	# Login page
	url(r'^login/$', login, {'template_name': 'users/login.html'}, name='login'),
	# Logout page
	url(r'^logout/$', views.logout_view, name='logout'),
	# New user registration
	url(r'^register/$', views.register, name='register'),
	# User profile info
	url(r'^profile/$', views.profile, name='profile')
]
