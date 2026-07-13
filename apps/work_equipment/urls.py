from django.urls import path

from . import views

app_name = 'work_equipment'

urlpatterns = [
    # Dashboard
    path('', views.WorkEquipmentDashboardView.as_view(), name='dashboard'),

    # Tipos de equipo
    path('tipos/', views.TipoEquipoListView.as_view(), name='tipo-list'),
    path('tipos/nuevo/', views.TipoEquipoCreateView.as_view(), name='tipo-create'),
    path('tipos/<int:pk>/editar/', views.TipoEquipoUpdateView.as_view(), name='tipo-update'),
    path('tipos/<int:pk>/eliminar/', views.TipoEquipoDeleteView.as_view(), name='tipo-delete'),

    # Inventario de equipos
    path('inventario/', views.EquipoTrabajoListView.as_view(), name='equipo-list'),
    path('inventario/nuevo/', views.EquipoTrabajoCreateView.as_view(), name='equipo-create'),
    path('inventario/<int:pk>/', views.EquipoTrabajoDetailView.as_view(), name='equipo-detail'),
    path('inventario/<int:pk>/editar/', views.EquipoTrabajoUpdateView.as_view(), name='equipo-update'),
    path('inventario/<int:pk>/eliminar/', views.EquipoTrabajoDeleteView.as_view(), name='equipo-delete'),

    # Revisiones
    path('revisiones/', views.RevisionEquipoListView.as_view(), name='revision-list'),
    path('revisiones/nueva/', views.RevisionEquipoCreateView.as_view(), name='revision-create'),
    path('revisiones/<int:pk>/editar/', views.RevisionEquipoUpdateView.as_view(), name='revision-update'),
    path('revisiones/<int:pk>/eliminar/', views.RevisionEquipoDeleteView.as_view(), name='revision-delete'),

    # Mantenimientos
    path('mantenimientos/', views.MantenimientoEquipoListView.as_view(), name='mantenimiento-list'),
    path('mantenimientos/nuevo/', views.MantenimientoEquipoCreateView.as_view(), name='mantenimiento-create'),
    path('mantenimientos/<int:pk>/editar/', views.MantenimientoEquipoUpdateView.as_view(), name='mantenimiento-update'),
    path('mantenimientos/<int:pk>/eliminar/', views.MantenimientoEquipoDeleteView.as_view(), name='mantenimiento-delete'),
]
