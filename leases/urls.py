"""Defines URL patters for leases"""

from django.conf.urls import include

from . import views
from django.urls import path

app_name = 'leases'

urlpatterns = [
	# Inventory page
	path('inventory/<int:pk>', views.inventory, name='inventory'),
]
