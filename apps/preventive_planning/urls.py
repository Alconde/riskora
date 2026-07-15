from django.urls import path

from . import views

app_name = 'preventive_planning'

urlpatterns = [
    path('', views.PlanificacionDashboardView.as_view(), name='dashboard'),
    path('items/', views.ItemPlanificacionListView.as_view(), name='item-list'),
    path('items/nuevo/', views.ItemPlanificacionCreateView.as_view(), name='item-create'),
    path('items/<int:pk>/', views.ItemPlanificacionDetailView.as_view(), name='item-detail'),
    path('items/<int:pk>/editar/', views.ItemPlanificacionUpdateView.as_view(), name='item-update'),
    path('items/<int:pk>/eliminar/', views.ItemPlanificacionDeleteView.as_view(), name='item-delete'),
    path('importar/', views.importar_excel, name='importar'),
    path('plantilla/', views.plantilla_excel, name='plantilla'),
    path('exportar/', views.exportar_excel, name='exportar'),
    path('catalogo/', views.MedidaCatalogoListView.as_view(), name='catalogo-list'),
    path('catalogo/nuevo/', views.MedidaCatalogoCreateView.as_view(), name='catalogo-create'),
    path('catalogo/<int:pk>/editar/', views.MedidaCatalogoUpdateView.as_view(), name='catalogo-update'),
    path('catalogo/<int:pk>/eliminar/', views.MedidaCatalogoDeleteView.as_view(), name='catalogo-delete'),
]
