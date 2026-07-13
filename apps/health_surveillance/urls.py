from django.urls import path
from . import views

app_name = 'health_surveillance'

urlpatterns = [
    path('', views.ReconocimientoMedicoListView.as_view(), name='list'),
    path('nuevo/', views.ReconocimientoMedicoCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ReconocimientoMedicoDetailView.as_view(), name='detail'),
    path('<int:pk>/editar/', views.ReconocimientoMedicoUpdateView.as_view(), name='update'),
    path('<int:pk>/eliminar/', views.ReconocimientoMedicoDeleteView.as_view(), name='delete'),
    path('controles/', views.ControlSaludListView.as_view(), name='controles'),
    path('controles/nuevo/', views.ControlSaludCreateView.as_view(), name='control-create'),
    path('controles/<int:pk>/eliminar/', views.ControlSaludDeleteView.as_view(), name='control-delete'),
]
