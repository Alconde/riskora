from django.urls import path

from . import views

app_name = 'audits'

urlpatterns = [
    # Dashboard
    path('', views.AuditoriasDashboardView.as_view(), name='dashboard'),

    # Programas de auditoría
    path('programas/', views.ProgramaAuditoriaListView.as_view(), name='programa_list'),
    path('programas/nuevo/', views.ProgramaAuditoriaCreateView.as_view(), name='programa_create'),
    path('programas/<int:pk>/', views.ProgramaAuditoriaDetailView.as_view(), name='programa_detail'),
    path('programas/<int:pk>/editar/', views.ProgramaAuditoriaUpdateView.as_view(), name='programa_update'),
    path('programas/<int:pk>/eliminar/', views.ProgramaAuditoriaDeleteView.as_view(), name='programa_delete'),

    # Auditorías internas
    path('auditorias/', views.AuditoriaInternaListView.as_view(), name='auditoria_list'),
    path('auditorias/nueva/', views.AuditoriaInternaCreateView.as_view(), name='auditoria_create'),
    path('auditorias/<int:pk>/', views.AuditoriaInternaDetailView.as_view(), name='auditoria_detail'),
    path('auditorias/<int:pk>/editar/', views.AuditoriaInternaUpdateView.as_view(), name='auditoria_update'),
    path('auditorias/<int:pk>/eliminar/', views.AuditoriaInternaDeleteView.as_view(), name='auditoria_delete'),

    # Checklist
    path('auditorias/<int:auditoria_pk>/checklist/nuevo/', views.ChecklistCreateView.as_view(), name='checklist_create'),
    path('auditorias/<int:auditoria_pk>/checklist/carga-masiva/', views.ChecklistBulkCreateView.as_view(), name='checklist_bulk'),
    path('checklist/<int:pk>/editar/', views.ChecklistUpdateView.as_view(), name='checklist_update'),

    # Informes
    path('auditorias/<int:auditoria_pk>/informe/nuevo/', views.InformeAuditoriaCreateView.as_view(), name='informe_create'),
    path('informes/<int:pk>/', views.InformeAuditoriaDetailView.as_view(), name='informe_detail'),
    path('informes/<int:pk>/editar/', views.InformeAuditoriaUpdateView.as_view(), name='informe_update'),
]
