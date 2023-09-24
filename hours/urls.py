"""Defines URL patterns for hours"""
from . import views
from django.urls import path

app_name = 'hours'

urlpatterns = [
		path('', views.index, name='index'),
	]
