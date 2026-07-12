from django.urls import path

from apps.workcenters.views import (
    WorkCenterListView,
    WorkCenterDetailView,
    WorkCenterCreateView,
    WorkCenterUpdateView,
)

urlpatterns = [
    path('', WorkCenterListView.as_view(), name='workcenter-list'),
    path('nuevo/', WorkCenterCreateView.as_view(), name='workcenter-create'),
    path('<int:pk>/', WorkCenterDetailView.as_view(), name='workcenter-detail'),
    path('<int:pk>/editar/', WorkCenterUpdateView.as_view(), name='workcenter-update'),
]