from django.urls import path
from .views import TaskListView, TaskDetailView, AlertDetailView

app_name = 'tasks'

urlpatterns = [
    path('tasks/', TaskListView.as_view(), name='list'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='detail'),
    path('alerts/<int:pk>/', AlertDetailView.as_view(), name='alert_detail'),
]