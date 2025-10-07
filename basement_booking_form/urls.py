from django.urls import path
from . import views

app_name = 'basement_booking_form'

urlpatterns = [
    path('basement_booking_form/', views.BasementBookingFormView.as_view(), name='basement_booking_form'),
]
