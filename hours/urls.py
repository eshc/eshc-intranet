"""Defines URL patterns for hours"""

from django.urls import path
from . import views

app_name = "hours"

urlpatterns = [
    path("", views.index, name="index"),
]
