from django.urls import path
from . import views

app_name = 'chemical_products'

urlpatterns = [
    path('', views.ProductoQuimicoListView.as_view(), name='list'),
    path('nuevo/', views.ProductoQuimicoCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ProductoQuimicoDetailView.as_view(), name='detail'),
    path('<int:pk>/editar/', views.ProductoQuimicoUpdateView.as_view(), name='update'),
    path('<int:pk>/eliminar/', views.ProductoQuimicoDeleteView.as_view(), name='delete'),
    path('<int:producto_pk>/clasificacion/nueva/', views.ClasificacionQuimicaCreateView.as_view(), name='clasificacion-create'),
    path('clasificacion/<int:pk>/eliminar/', views.ClasificacionQuimicaDeleteView.as_view(), name='clasificacion-delete'),
]
