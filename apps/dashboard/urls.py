from django.urls import path

app_name = 'dashboard'

from apps.dashboard.views import DashboardView, DashboardChartDataView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('api/chart-data/', DashboardChartDataView.as_view(), name='chart-data'),
]