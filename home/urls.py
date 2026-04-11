"""Defines URL patterns for home"""

from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "home"

urlpatterns = [
    # Home page
    path("", views.index, name="index"),
    # User profile editing
    path("accounts/edit_profile/", views.edit_profile, name="edit_profile"),
    path("accounts/signup/", views.MySignupView.as_view()),
    path("map/", views.map, name="map"),
    path("gms/", views.gms, name="gms"),
    path("archive/", views.archive, name="archive"),
    path("gms/<int:pk>/", views.agenda, name="agenda"),
    path("gms/<int:id>/submit/", views.submit, name="submit"),
    path("gms/<int:id>/submit_update/", views.submit_update, name="submit_update"),
    path("gms/<int:id>/upload_minutes/", views.upload_minutes, name="upload_minutes"),
    path("gms/<int:pk>/delete/", views.delete, name="delete"),
    path("groups/", views.groups, name="groups"),
    path("cash/", views.cash, name="cash"),
    path("wsp/", views.wsp, name="wsp"),
    path("wsp_subgroups/", views.wsp_subgroups, name="wsp_subgroups"),
    path("laundry/", views.laundry, name="laundry"),
    path(
        "taskforces/",
        RedirectView.as_view(url="/wiki/work-share-plan/taskforces/", permanent=True),
        name="taskforces",
    ),
]
