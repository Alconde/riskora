from django.urls import path
from .views import (
    TaskListView,
    TaskDetailView,
    TaskCreateView,
    TaskUpdateView,
    TaskDeleteView,
    TaskCompleteView,
    AlertListView,
    AlertDetailView,
    AlertDismissView,
)

app_name = 'tasks'

urlpatterns = [
    path('tasks/', TaskListView.as_view(), name='list'),
    path('tasks/nueva/', TaskCreateView.as_view(), name='create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='detail'),
    path('tasks/<int:pk>/editar/', TaskUpdateView.as_view(), name='update'),
    path('tasks/<int:pk>/eliminar/', TaskDeleteView.as_view(), name='delete'),
    path('tasks/<int:pk>/completar/', TaskCompleteView.as_view(), name='complete'),
    path('alertas/', AlertListView.as_view(), name='alert-list'),
    path('alertas/<int:pk>/', AlertDetailView.as_view(), name='alert_detail'),
    path('alertas/<int:pk>/cerrar/', AlertDismissView.as_view(), name='alert-dismiss'),
]
