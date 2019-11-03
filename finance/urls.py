from django.urls import path

import finance.views as views

urlpatterns = [
    path('', views.financial_overview),
]

