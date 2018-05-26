"""Defines URL patterns for home"""

from django.conf.urls import url

from . import views

urlpatterns = [
	# Home page
	url(r'^$', views.index, name='index'),
	url(r'^mail/$', views.mail_test, name='mail_test'),
	# User profile editing
	url(r'^accounts/edit_profile/$', views.edit_profile, name='edit_profile'),
	url(r'^accounts/signup/$', views.MySignupView.as_view()),

	url(r'^map/$', views.map, name='map'),
	url(r'^gms/$', views.gms, name='gms'),
	url(r'^archive/$', views.archive, name='archive'),
    url(r'^gms/(?P<pk>[0-9]+)/$', views.agenda, name='agenda'),
    url(r'^gms/(?P<id>[0-9]+)/submit/$', views.submit, name='submit'),
    url(r'^gms/(?P<id>[0-9]+)/submit_update/$', views.submit_update, name='submit_update'),
    url(r'^gms/(?P<id>[0-9]+)/upload_minutes/$', views.upload_minutes, name='upload_minutes'),
    url(r'^gms/(?P<pk>[0-9]+)/delete/$', views.delete, name='delete'),
    url(r'^groups/$', views.groups, name='groups'),
    url(r'^cash/$', views.cash, name='cash'),
    url(r'^wsp/$', views.wsp, name='wsp'),


]
