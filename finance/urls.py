from django.urls import path

import finance.views as views

urlpatterns = [
    path('', views.financial_overview, name='fin-overview'),
    path('qbo_callback', views.qbo_callback_view, name='fin-qbo-callback'),
]

