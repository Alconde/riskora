from django.urls import path

from . import views

app_name = 'legal_requirements'

urlpatterns = [
    # Dashboard
    path('', views.LegalDashboardView.as_view(), name='dashboard'),

    # Alertas
    path('alertas/', views.AlertaLegalListView.as_view(), name='alerta_list'),
    path('alertas/<int:pk>/marcar-leida/', views.AlertaLegalMarcarLeidaView.as_view(), name='alerta_marcar_leida'),
    path('alertas/<int:pk>/resolver/', views.AlertaLegalResolverView.as_view(), name='alerta_resolver'),

    # Normativa
    path('normativa/', views.NormativaLegalListView.as_view(), name='normativa_list'),
    path('normativa/nueva/', views.NormativaLegalCreateView.as_view(), name='normativa_create'),
    path('normativa/<int:pk>/', views.NormativaLegalDetailView.as_view(), name='normativa_detail'),
    path('normativa/<int:pk>/editar/', views.NormativaLegalUpdateView.as_view(), name='normativa_update'),
    path('normativa/<int:pk>/eliminar/', views.NormativaLegalDeleteView.as_view(), name='normativa_delete'),

    # Requisitos legales
    path('requisitos/', views.RequisitoLegalListView.as_view(), name='requisito_list'),
    path('requisitos/nuevo/', views.RequisitoLegalCreateView.as_view(), name='requisito_create'),
    path('requisitos/<int:pk>/editar/', views.RequisitoLegalUpdateView.as_view(), name='requisito_update'),

    # Cumplimiento legal
    path('cumplimiento/', views.CumplimientoLegalListView.as_view(), name='cumplimiento_list'),
    path('cumplimiento/nuevo/', views.CumplimientoLegalCreateView.as_view(), name='cumplimiento_create'),
    path('cumplimiento/<int:pk>/editar/', views.CumplimientoLegalUpdateView.as_view(), name='cumplimiento_update'),
    path('cumplimiento/carga-masiva/', views.CumplimientoBulkCreateView.as_view(), name='cumplimiento_bulk'),
]
