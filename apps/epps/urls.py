from django.urls import path

from . import views

app_name = 'epps'

urlpatterns = [
    # Dashboard
    path('', views.EppsDashboardView.as_view(), name='dashboard'),

    # Enfermedades profesionales
    path('enfermedades/', views.EnfermedadProfesionalListView.as_view(), name='enfermedad-list'),
    path('enfermedades/nueva/', views.EnfermedadProfesionalCreateView.as_view(), name='enfermedad-create'),
    path('enfermedades/<int:pk>/', views.EnfermedadProfesionalDetailView.as_view(), name='enfermedad-detail'),
    path('enfermedades/<int:pk>/editar/', views.EnfermedadProfesionalUpdateView.as_view(), name='enfermedad-update'),
    path('enfermedades/<int:pk>/eliminar/', views.EnfermedadProfesionalDeleteView.as_view(), name='enfermedad-delete'),

    # Investigacion
    path(
        'enfermedades/<int:eepp_pk>/investigacion/nueva/',
        views.InvestigacionEEPPCreateView.as_view(),
        name='investigacion-create',
    ),
    path(
        'investigacion/<int:pk>/editar/',
        views.InvestigacionEEPPUpdateView.as_view(),
        name='investigacion-update',
    ),
    path(
        'investigacion/<int:pk>/',
        views.InvestigacionEEPPDetailView.as_view(),
        name='investigacion-detail',
    ),
    path('investigacion/imprimir-blanco/', views.imprimir_eepp_blanco, name='investigacion-blanco-pdf'),
    path('investigacion/<int:pk>/pdf/', views.descargar_eepp_pdf, name='investigacion-pdf'),

    # Procedimiento
    path('procedimiento/nuevo/', views.ProcedimientoEEPPCreateView.as_view(), name='procedimiento-create'),
    path('procedimiento/<int:pk>/editar/', views.ProcedimientoEEPPUpdateView.as_view(), name='procedimiento-update'),
]
