from django.urls import path

from apps.companies.views import (
    CompanyListView,
    CompanyDetailView,
    CompanyCreateView,
    CompanyUpdateView,
)
from .views import switch_company



urlpatterns = [
    path('', CompanyListView.as_view(), name='company-list'),
    path('nuevo/', CompanyCreateView.as_view(), name='company-create'),
    path('<int:pk>/', CompanyDetailView.as_view(), name='company-detail'),
    path('<int:pk>/editar/', CompanyUpdateView.as_view(), name='company-update'),
    path('switch/<int:company_id>/', switch_company, name='company-switch'),
]