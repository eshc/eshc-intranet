"""Defines URL patters for leases"""

from django.conf.urls import url, include

from . import views

app_name = 'leases'

urlpatterns = [
	# Inventory page
	url(r'^inventory/(?P<pk>[0-9]+)$', views.inventory, name='inventory'),
	url(r'^covid/(?P<pk>[0-9]+)$', views.covid, name='covid'),
]
