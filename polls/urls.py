from . import views
from django.urls import path

app_name = 'polls'

urlpatterns = [
		path('', views.index, name='index'),
		path('submit/', views.submit, name='submit'),
	    path('<int:pk>/delete/', views.delete, name='delete'),
	    path('<int:pk>/', views.detail, name='detail'),
	]
