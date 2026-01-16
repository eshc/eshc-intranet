"""Defines URL patters for leases"""

from django.urls import path

from . import views

app_name = 'leases'

urlpatterns = [
	# Inventory page
	path('inventory/<int:pk>', views.inventory, name='inventory'),
]
