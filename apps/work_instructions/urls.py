from django.urls import path
from . import views

app_name = 'work_instructions'

urlpatterns = [
    path('', views.InstruccionTrabajoListView.as_view(), name='list'),
    path('nueva/', views.InstruccionTrabajoCreateView.as_view(), name='create'),
    path('<int:pk>/', views.InstruccionTrabajoDetailView.as_view(), name='detail'),
    path('<int:pk>/editar/', views.InstruccionTrabajoUpdateView.as_view(), name='update'),
    path('<int:pk>/eliminar/', views.InstruccionTrabajoDeleteView.as_view(), name='delete'),
]
