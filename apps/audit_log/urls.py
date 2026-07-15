from django.urls import path

from apps.audit_log.views import AuditLogListView, AuditLogDetailView

app_name = 'audit_log'

urlpatterns = [
    path('', AuditLogListView.as_view(), name='log-list'),
    path('<int:pk>/', AuditLogDetailView.as_view(), name='log-detail'),
]
