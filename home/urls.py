"""Defines URL patterns for home"""

from django.conf.urls import url

from . import views

urlpatterns = [
	# Home page
	url(r'^$', views.index, name='index'),
	url(r'^mail/$', views.mail_test, name='mail_test'),
	# User profile editing
	url(r'^accounts/edit_profile/$', views.edit_profile, name='edit_profile'),

	url(r'^map/$', views.map, name='map'),
]
