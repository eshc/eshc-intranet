"""Defines URL patterns for hours"""

from django.conf.urls import url
from . import views

app_name = 'hours'

urlpatterns = [
		url(r'^$', views.index, name='index'),
	]
