from django.urls import path

from . import views

app_name = 'authorizations'

urlpatterns = [
    path('', views.AutorizacionDashboardView.as_view(), name='dashboard'),
    path('requisitos/nuevo/', views.RequisitoAutorizacionCreateView.as_view(), name='requisito-create'),
    path('requisitos/<int:pk>/', views.RequisitoAutorizacionDetailView.as_view(), name='requisito-detail'),
    path('requisitos/<int:pk>/editar/', views.RequisitoAutorizacionUpdateView.as_view(), name='requisito-update'),
    path('requisitos/<int:pk>/eliminar/', views.RequisitoAutorizacionDeleteView.as_view(), name='requisito-delete'),
    path('requisitos/<int:requisito_pk>/nueva/', views.AutorizacionCreateView.as_view(), name='autorizacion-create'),
    path('autorizaciones/<int:pk>/editar/', views.AutorizacionUpdateView.as_view(), name='autorizacion-update'),
    path('autorizaciones/<int:pk>/eliminar/', views.AutorizacionDeleteView.as_view(), name='autorizacion-delete'),
    path('trabajador/<int:pk>/', views.WorkerAutorizacionesView.as_view(), name='worker-autorizaciones'),
]
