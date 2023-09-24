"""Defines URL patters for users"""

from django.conf.urls import include
from django.contrib.auth.views import login

from . import views
from django.urls import path

app_name = 'users'

urlpatterns = [
	# Login page
	path('login/', login, {'template_name': 'users/login.html'}, name='login'),
	# Logout page
	path('logout/', views.logout_view, name='logout'),
	# New user registration
	path('register/', views.register, name='register'),
	# User profile info
	path('profile/', views.profile, name='profile'),
	# User profile editing
	path('edit_profile/', views.edit_profile, name='edit_profile')
]
