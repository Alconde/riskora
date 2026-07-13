from django.urls import path

from . import views

app_name = 'inspections'

urlpatterns = [
    # Plantillas
    path('plantillas/', views.PlantillaListView.as_view(), name='plantilla-list'),
    path('plantillas/nueva/', views.PlantillaCreateView.as_view(), name='plantilla-create'),
    path('plantillas/<int:pk>/', views.PlantillaDetailView.as_view(), name='plantilla-detail'),
    path('plantillas/<int:pk>/editar/', views.PlantillaUpdateView.as_view(), name='plantilla-update'),
    path('plantillas/<int:pk>/eliminar/', views.PlantillaDeleteView.as_view(), name='plantilla-delete'),
    path('plantillas/<int:plantilla_pk>/item/nuevo/', views.PlantillaItemCreateView.as_view(), name='plantilla-item-create'),

    # Inspecciones
    path('', views.InspeccionListView.as_view(), name='inspeccion-list'),
    path('nueva/', views.InspeccionCreateView.as_view(), name='inspeccion-create'),
    path('<int:pk>/', views.InspeccionDetailView.as_view(), name='inspeccion-detail'),
    path('<int:pk>/editar/', views.InspeccionUpdateView.as_view(), name='inspeccion-update'),
    path('<int:pk>/eliminar/', views.InspeccionDeleteView.as_view(), name='inspeccion-delete'),

    # Items de inspeccion
    path('<int:inspeccion_pk>/item/nuevo/', views.InspeccionItemCreateView.as_view(), name='item-create'),
    path('items/<int:pk>/editar/', views.InspeccionItemUpdateView.as_view(), name='item-update'),
    path('items/<int:pk>/eliminar/', views.InspeccionItemDeleteView.as_view(), name='item-delete'),
    path('items/<int:item_pk>/nc/', views.InspeccionItemNCView.as_view(), name='item-nc'),
]
