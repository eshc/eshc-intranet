"""Defines URL patterns for whiteboard"""

from django.conf.urls import url

from . import views

app_name = 'whiteboard'

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^new/$', views.add_note, name='add_note'),
]
