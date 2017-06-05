"""Defines URL patterns for home"""

from django.conf.urls import url

from . import views

urlpatterns = [
	# Home page
	url(r'^$', views.index, name='index'),
	url(r'^mail/$', views.mail_test, name='mail_test'),
]
