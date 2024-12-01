from django.urls import path
from . import views

app_name = 'census'

urlpatterns = [
    path('census/<int:session_id>/', views.ApplyView.as_view(), name='census'),
]
