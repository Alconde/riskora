from django.urls import path

app_name = 'workers'

from apps.workers.views import (
    WorkerListView,
    WorkerDetailView,
    WorkerCreateView,
    WorkerUpdateView,
    WorkerDeleteView,
    WorkerDocumentsView,
    JobPositionListView,
    JobPositionDetailView,
    JobPositionCreateView,
    JobPositionUpdateView,
    JobPositionDeleteView,
    load_workcenters,
    load_jobpositions,
)

urlpatterns = [
    path('', WorkerListView.as_view(), name='worker-list'),
    path('documentos/', WorkerDocumentsView.as_view(), name='worker-documents'),
    path('nuevo/', WorkerCreateView.as_view(), name='worker-create'),
    path('<int:pk>/', WorkerDetailView.as_view(), name='worker-detail'),
    path('<int:pk>/editar/', WorkerUpdateView.as_view(), name='worker-update'),
    path('<int:pk>/eliminar/', WorkerDeleteView.as_view(), name='worker-delete'),

    path('puestos/', JobPositionListView.as_view(), name='jobposition-list'),
    path('puestos/nuevo/', JobPositionCreateView.as_view(), name='jobposition-create'),
    path('puestos/<int:pk>/', JobPositionDetailView.as_view(), name='jobposition-detail'),
    path('puestos/<int:pk>/editar/', JobPositionUpdateView.as_view(), name='jobposition-update'),
    path('puestos/<int:pk>/eliminar/', JobPositionDeleteView.as_view(), name='jobposition-delete'),

    path('ajax/load-workcenters/', load_workcenters, name='ajax-load-workcenters'),
    path('ajax/load-jobpositions/', load_jobpositions, name='ajax-load-jobpositions'),
]