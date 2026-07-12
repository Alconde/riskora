from django.urls import path

app_name = 'dashboard'

from apps.dashboard.views import DashboardView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard-home'),
]