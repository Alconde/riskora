from django.urls import path

app_name = 'companies'

from apps.companies.views import (
    CompanyListView,
    CompanyDetailView,
    CompanyCreateView,
    CompanyUpdateView,
    CompanyDeleteView,
)
from .views import switch_company



urlpatterns = [
    path('', CompanyListView.as_view(), name='company-list'),
    path('nuevo/', CompanyCreateView.as_view(), name='company-create'),
    path('<int:pk>/', CompanyDetailView.as_view(), name='company-detail'),
    path('<int:pk>/editar/', CompanyUpdateView.as_view(), name='company-update'),
    path('<int:pk>/eliminar/', CompanyDeleteView.as_view(), name='company-delete'),
    path('switch/', switch_company, name='company-switch'),
    path('switch/<int:company_id>/', switch_company, name='company-switch-id'),
]