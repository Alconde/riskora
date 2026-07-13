from django.urls import path
from . import views

app_name = 'emergency_measures'

urlpatterns = [
    path('', views.MedidaEmergenciaListView.as_view(), name='list'),
    path('nueva/', views.MedidaEmergenciaCreateView.as_view(), name='create'),
    path('<int:pk>/', views.MedidaEmergenciaDetailView.as_view(), name='detail'),
    path('<int:pk>/editar/', views.MedidaEmergenciaUpdateView.as_view(), name='update'),
    path('<int:pk>/eliminar/', views.MedidaEmergenciaDeleteView.as_view(), name='delete'),
    path('simulacro/nuevo/', views.HistorialSimulacroCreateView.as_view(), name='simulacro-create'),
]
