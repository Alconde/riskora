from django.urls import path

from . import views

app_name = 'incidents'

urlpatterns = [
    # Dashboard
    path('', views.IncidentsDashboardView.as_view(), name='dashboard'),

    # Accidentes
    path('accidentes/', views.AccidenteListView.as_view(), name='accidente-list'),
    path('accidentes/nuevo/', views.AccidenteCreateView.as_view(), name='accidente-create'),
    path('accidentes/<int:pk>/', views.AccidenteDetailView.as_view(), name='accidente-detail'),
    path('accidentes/<int:pk>/editar/', views.AccidenteUpdateView.as_view(), name='accidente-update'),
    path('accidentes/<int:pk>/eliminar/', views.AccidenteDeleteView.as_view(), name='accidente-delete'),
    path('accidentes/<int:accidente_pk>/nc/', views.AccidenteNCView.as_view(), name='accidente-nc'),

    # Investigacion
    path(
        'accidentes/<int:accidente_pk>/investigacion/nueva/',
        views.InvestigacionCreateView.as_view(),
        name='investigacion-create',
    ),
    path(
        'investigacion/<int:pk>/editar/',
        views.InvestigacionUpdateView.as_view(),
        name='investigacion-update',
    ),
    path(
        'investigacion/<int:pk>/',
        views.InvestigacionDetailView.as_view(),
        name='investigacion-detail',
    ),
    path('investigacion/imprimir-blanco/', views.imprimir_investigacion_blanco, name='investigacion-blanco-pdf'),
    path('investigacion/<int:pk>/pdf/', views.descargar_investigacion_pdf, name='investigacion-pdf'),

    # Causas
    path('causas/', views.CausaListView.as_view(), name='causa-list'),
    path('causas/nueva/', views.CausaCreateView.as_view(), name='causa-create'),
    path('causas/<int:pk>/editar/', views.CausaUpdateView.as_view(), name='causa-update'),
    path('causas/<int:pk>/eliminar/', views.CausaDeleteView.as_view(), name='causa-delete'),

    # Incidentes
    path('incidentes/', views.IncidenteListView.as_view(), name='incidente-list'),
    path('incidentes/nuevo/', views.IncidenteCreateView.as_view(), name='incidente-create'),
    path('incidentes/<int:pk>/', views.IncidenteDetailView.as_view(), name='incidente-detail'),
    path('incidentes/<int:pk>/editar/', views.IncidenteUpdateView.as_view(), name='incidente-update'),
    path('incidentes/<int:pk>/eliminar/', views.IncidenteDeleteView.as_view(), name='incidente-delete'),

    # Procedimiento
    path('procedimiento/nuevo/', views.ProcedimientoInvestigacionCreateView.as_view(), name='procedimiento-create'),
    path('procedimiento/<int:pk>/editar/', views.ProcedimientoInvestigacionUpdateView.as_view(), name='procedimiento-update'),
]
