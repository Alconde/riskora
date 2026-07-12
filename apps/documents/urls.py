from django.urls import path

from .views import (
    DocumentListView,
    DocumentDetailView,
    DocumentCreateView,
    DocumentUpdateView,
    DocumentDeleteView,
)

app_name = 'documents'

urlpatterns = [
    path('', DocumentListView.as_view(), name='list'),
    path('new/', DocumentCreateView.as_view(), name='create'),
    path('<uuid:pk>/', DocumentDetailView.as_view(), name='detail'),
    path('<uuid:pk>/edit/', DocumentUpdateView.as_view(), name='update'),
    path('<uuid:pk>/delete/', DocumentDeleteView.as_view(), name='delete'),
]