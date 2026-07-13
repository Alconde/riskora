from django.urls import path

from . import views

app_name = 'epis'

urlpatterns = [
    # Dashboard principal
    path('', views.EPIDashboardView.as_view(), name='dashboard'),

    # Procedimiento
    path('procedimiento/nuevo/', views.ProcedimientoEntregaCreateView.as_view(), name='procedimiento-create'),
    path('procedimiento/<int:pk>/editar/', views.ProcedimientoEntregaUpdateView.as_view(), name='procedimiento-update'),

    # Firmas por trabajador
    path('firmas/', views.FirmaTrabajadorListView.as_view(), name='firma-trabajador-list'),
    path('firmas/nueva/', views.FirmaEntregaCreateView.as_view(), name='firma-create'),
    path('firmas/<int:pk>/subir/', views.FirmaEntregaUploadView.as_view(), name='firma-upload'),

    # Registro PDF
    path('registro-pdf/', views.descargar_registro_entregas_pdf, name='registro-pdf'),

    # Catalogo de EPIs del mercado
    path('catalogo/', views.CatalogoEPIListView.as_view(), name='catalogo-list'),
    path('catalogo/<int:pk>/', views.CatalogoEPIDetailView.as_view(), name='catalogo-detail'),

    # Inventario de EPIs (empresa)
    path('inventario/', views.EPIListView.as_view(), name='epi-list'),
    path('inventario/nuevo/', views.EPICreateView.as_view(), name='epi-create'),
    path('inventario/<int:pk>/', views.EPIDetailView.as_view(), name='epi-detail'),
    path('inventario/<int:pk>/editar/', views.EPIUpdateView.as_view(), name='epi-update'),
    path('inventario/<int:pk>/eliminar/', views.EPIDeleteView.as_view(), name='epi-delete'),

    # Entregas
    path('entregas/', views.EntregaEPIListView.as_view(), name='entrega-list'),
    path('entregas/nueva/', views.EntregaEPICreateView.as_view(), name='entrega-create'),
    path('entregas/<int:pk>/', views.EntregaEPIDetailView.as_view(), name='entrega-detail'),
    path('entregas/<int:pk>/editar/', views.EntregaEPIUpdateView.as_view(), name='entrega-update'),
    path('entregas/<int:pk>/eliminar/', views.EntregaEPIDeleteView.as_view(), name='entrega-delete'),

    # Inspecciones
    path('inspecciones/', views.InspeccionEPIListView.as_view(), name='inspeccion-list'),
    path('inspecciones/nueva/', views.InspeccionEPICreateView.as_view(), name='inspeccion-create'),
    path('inspecciones/<int:pk>/', views.InspeccionEPIDetailView.as_view(), name='inspeccion-detail'),
    path('inspecciones/<int:pk>/editar/', views.InspeccionEPIUpdateView.as_view(), name='inspeccion-update'),
    path('inspecciones/<int:pk>/eliminar/', views.InspeccionEPIDeleteView.as_view(), name='inspeccion-delete'),
]
