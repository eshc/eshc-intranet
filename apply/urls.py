from django.urls import path
from . import views

app_name = 'apply'

urlpatterns = [
    path('apply/<int:session_id>/', views.ApplyView.as_view(), name='apply-form'),
    path('vote/<int:session_id>/', views.VoteView.as_view(), name='vote-form')
]
