from django.urls import path

from apps.workers.views import (
    WorkerListView,
    WorkerDetailView,
    WorkerCreateView,
    WorkerUpdateView,
    JobPositionListView,
    JobPositionDetailView,
    JobPositionCreateView,
    JobPositionUpdateView,
    load_workcenters,
    load_jobpositions,
)

urlpatterns = [
    path('', WorkerListView.as_view(), name='worker-list'),
    path('nuevo/', WorkerCreateView.as_view(), name='worker-create'),
    path('<int:pk>/', WorkerDetailView.as_view(), name='worker-detail'),
    path('<int:pk>/editar/', WorkerUpdateView.as_view(), name='worker-update'),

    path('puestos/', JobPositionListView.as_view(), name='jobposition-list'),
    path('puestos/nuevo/', JobPositionCreateView.as_view(), name='jobposition-create'),
    path('puestos/<int:pk>/', JobPositionDetailView.as_view(), name='jobposition-detail'),
    path('puestos/<int:pk>/editar/', JobPositionUpdateView.as_view(), name='jobposition-update'),

    path('ajax/load-workcenters/', load_workcenters, name='ajax-load-workcenters'),
    path('ajax/load-jobpositions/', load_jobpositions, name='ajax-load-jobpositions'),
]