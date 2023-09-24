"""Defines URL patterns for home"""
from . import views
from django.urls import path

app_name = 'home'

urlpatterns = [
	# Home page
	path('', views.index, name='index'),
	path('mail/', views.mail_test, name='mail_test'),
	# User profile editing
	path('accounts/edit_profile/', views.edit_profile, name='edit_profile'),
	path('accounts/signup/', views.MySignupView.as_view()),

	path('map/', views.map, name='map'),
	path('gms/', views.gms, name='gms'),
	path('archive/', views.archive, name='archive'),
    path('gms/<int:pk>/', views.agenda, name='agenda'),
    path('gms/<int:id>/submit/', views.submit, name='submit'),
    path('gms/<int:id>/submit_update/', views.submit_update, name='submit_update'),
    path('gms/<int:id>/upload_minutes/', views.upload_minutes, name='upload_minutes'),
    path('gms/<int:pk>/delete/', views.delete, name='delete'),
    path('groups/', views.groups, name='groups'),
    path('cash/', views.cash, name='cash'),
    path('wsp/', views.wsp, name='wsp'),
    path('wsp_subgroups/', views.wsp_subgroups, name='wsp_subgroups'),
    path('laundry/', views.laundry, name='laundry'),
    path('taskforces/', views.taskforces,name='taskforces')
]
