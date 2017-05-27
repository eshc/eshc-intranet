"""Defines URL patters for leases"""

from django.conf.urls import url, include
from django.contrib.auth.views import login

from . import views

urlpatterns = [
	# Inventory page
	url(r'^inventory/(?P<pk>[0-9]+)$', views.inventory, name='inventory'),
]
