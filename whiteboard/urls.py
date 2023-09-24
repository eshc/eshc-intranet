"""Defines URL patterns for whiteboard"""

from . import views
from django.urls import path

app_name = 'whiteboard'

urlpatterns = [
	path('', views.index, name='index'),
	path('new/', views.add_note, name='add_note'),
]
