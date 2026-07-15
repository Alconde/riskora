from django.urls import path
from . import views

app_name = 'cae'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('empresas/', views.EmpresaListView.as_view(), name='empresa-list'),
    path('empresas/nueva/', views.EmpresaCreateView.as_view(), name='empresa-create'),
    path('empresas/<int:pk>/', views.EmpresaDetailView.as_view(), name='empresa-detail'),
    path('empresas/<int:pk>/editar/', views.EmpresaUpdateView.as_view(), name='empresa-update'),
    path('empresas/<int:pk>/eliminar/', views.EmpresaDeleteView.as_view(), name='empresa-delete'),
    path('documento/<int:pk>/editar/', views.DocumentoCAEUpdateView.as_view(), name='documento-update'),
    path('documento/<int:empresa_subcontrata_id>/nuevo/<int:tipo_id>/', views.DocumentoCAECreateView.as_view(), name='documento-create'),
    path('documento/<int:pk>/descargar/', views.download_documento_cae, name='documento-download'),
    path('procedimiento/', views.ProcedimientoCAEUpdateView.as_view(), name='procedimiento'),
    path('carta/', views.CartaCAEUpdateView.as_view(), name='carta'),
    path('riesgos/', views.DocumentoRiesgosCAEUpdateView.as_view(), name='riesgos'),
    path('descargar/procedimiento/<int:empresa_id>/', views.download_procedimiento_cae, name='procedimiento-download'),
    path('descargar/carta/<int:empresa_id>/', views.download_carta_cae, name='carta-download'),
    path('descargar/riesgos/<int:empresa_id>/', views.download_riesgos_cae, name='riesgos-download'),
]
