from django.urls import path
from . import views

app_name = 'emergency_measures'

urlpatterns = [
    path('', views.EmergencyDashboardView.as_view(), name='dashboard'),
    path('plan/', views.PlanAutoproteccionView.as_view(), name='plan-autoproteccion'),
    path('medios/', views.MediosProteccionView.as_view(), name='medios-proteccion'),
    path('medios/<int:pk>/editar/', views.EmpresaMedioProteccionUpdateView.as_view(), name='medio-update'),
    path('medios/<int:pk>/eliminar/', views.EmpresaMedioProteccionDeleteView.as_view(), name='medio-delete'),
    path('equipos/', views.EquiposEmergenciaListView.as_view(), name='equipos'),
    path('equipos/nuevo/', views.EquipoEmergenciaCreateView.as_view(), name='equipo-create'),
    path('equipos/<int:pk>/', views.EquipoEmergenciaDetailView.as_view(), name='equipo-detail'),
    path('equipos/<int:pk>/editar/', views.EquipoEmergenciaUpdateView.as_view(), name='equipo-update'),
    path('equipos/<int:pk>/eliminar/', views.EquipoEmergenciaDeleteView.as_view(), name='equipo-delete'),
    path('equipos/<int:equipo_pk>/miembro/nuevo/', views.MiembroEquipoCreateView.as_view(), name='miembro-create'),
    path('miembro/<int:pk>/eliminar/', views.MiembroEquipoDeleteView.as_view(), name='miembro-delete'),
    path('simulacros/', views.SimulacrosListView.as_view(), name='simulacros'),
    path('simulacros/nuevo/', views.SimulacroCreateView.as_view(), name='simulacro-create'),
    path('simulacros/<int:pk>/eliminar/', views.SimulacroDeleteView.as_view(), name='simulacro-delete'),
    path('entregas-info/', views.EntregasInfoListView.as_view(), name='entregas-info'),
    path('entregas-info/nueva/', views.EntregaInfoCreateView.as_view(), name='entrega-create'),
    path('entregas-info/<int:pk>/eliminar/', views.EntregaInfoDeleteView.as_view(), name='entrega-delete'),
]
