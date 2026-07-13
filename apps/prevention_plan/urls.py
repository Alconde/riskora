from django.urls import path
from . import views

app_name = 'prevention_plan'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('politica/', views.PoliticaUpdateView.as_view(), name='politica'),
    path('organigrama/', views.OrganigramaUpdateView.as_view(), name='organigrama'),
    path('delegado/', views.DelegadoUpdateView.as_view(), name='delegado'),
    path('recurso/', views.RecursoUpdateView.as_view(), name='recurso'),
    path('funciones/', views.FuncionesUpdateView.as_view(), name='funciones'),
    path('ett-teletrabajo/', views.ETTTeletrabajoUpdateView.as_view(), name='ett-teletrabajo'),
    path('descargar/politica/<int:plan_id>/', views.download_politica, name='download-politica'),
    path('descargar/organigrama/<int:plan_id>/', views.download_organigrama, name='download-organigrama'),
    path('descargar/delegado/<int:plan_id>/<str:doc_type>/', views.download_doc_delegado, name='download-delegado'),
    path('descargar/recurso/<int:plan_id>/<str:doc_type>/', views.download_doc_recurso, name='download-recurso'),
]
