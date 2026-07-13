from django.urls import path

from . import views

app_name = 'incidents'

urlpatterns = [
    # Accidentes
    path('', views.AccidenteListView.as_view(), name='accidente-list'),
    path('nuevo/', views.AccidenteCreateView.as_view(), name='accidente-create'),
    path('<int:pk>/', views.AccidenteDetailView.as_view(), name='accidente-detail'),
    path('<int:pk>/editar/', views.AccidenteUpdateView.as_view(), name='accidente-update'),
    path('<int:pk>/eliminar/', views.AccidenteDeleteView.as_view(), name='accidente-delete'),
    path('<int:accidente_pk>/nc/', views.AccidenteNCView.as_view(), name='accidente-nc'),

    # Investigacion
    path(
        '<int:accidente_pk>/investigacion/nueva/',
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
]
