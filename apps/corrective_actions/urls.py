from django.urls import path

from . import views

app_name = 'corrective_actions'

urlpatterns = [
    # No conformidades
    path('', views.NCListView.as_view(), name='nc-list'),
    path('exportar-excel/', views.exportar_ncs_excel, name='nc-export-excel'),
    path('nueva/', views.NCCreateView.as_view(), name='nc-create'),
    path('<int:pk>/', views.NCDetailView.as_view(), name='nc-detail'),
    path('<int:pk>/editar/', views.NCUpdateView.as_view(), name='nc-update'),
    path('<int:pk>/eliminar/', views.NCDeleteView.as_view(), name='nc-delete'),
    path('<int:pk>/cerrar/', views.NCCerrarView.as_view(), name='nc-close'),

    # Acciones correctivas
    path('acciones/', views.ACListView.as_view(), name='ac-list'),
    path('acciones/nueva/<int:nc_pk>/', views.ACCreateView.as_view(), name='ac-create'),
    path('acciones/<int:pk>/', views.ACDetailView.as_view(), name='ac-detail'),
    path('acciones/<int:pk>/editar/', views.ACUpdateView.as_view(), name='ac-update'),
    path('acciones/<int:pk>/eliminar/', views.ACDeleteView.as_view(), name='ac-delete'),

    # Acciones preventivas
    path('preventivas/', views.APListView.as_view(), name='ap-list'),
    path('preventivas/nueva/', views.APCreateView.as_view(), name='ap-create'),
    path('preventivas/<int:pk>/', views.APDetailView.as_view(), name='ap-detail'),
    path('preventivas/<int:pk>/editar/', views.APUpdateView.as_view(), name='ap-update'),
    path('preventivas/<int:pk>/eliminar/', views.APDeleteView.as_view(), name='ap-delete'),
]
