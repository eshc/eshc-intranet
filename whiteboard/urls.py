"""Defines URL patterns for whiteboard"""

from django.urls import path

from . import views

app_name = 'whiteboard'

urlpatterns = [
	path('', views.index, name='index'),
	path('new/', views.add_note, name='add_note'),
]
