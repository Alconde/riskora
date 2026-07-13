from django.urls import path
from . import views

app_name = 'company_data'

urlpatterns = [
    path('', views.CompanyDataDashboardView.as_view(), name='dashboard'),
]
