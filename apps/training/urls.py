from django.urls import path

from .views import (
    TrainingCategoryCreateView,
    TrainingCategoryDeleteView,
    TrainingCategoryListView,
    TrainingCategoryUpdateView,
    TrainingCourseCreateView,
    TrainingCourseDeleteView,
    TrainingCourseDetailView,
    TrainingCourseListView,
    TrainingCourseUpdateView,
    TrainingRecordCreateView,
    TrainingRecordDeleteView,
    TrainingRecordDetailView,
    TrainingRecordListView,
    TrainingRecordUpdateView,
    TrainingDashboardView,
    exportar_formacion_excel,
)

app_name = 'training'

urlpatterns = [
    # categorías
    path('dashboard/', TrainingDashboardView.as_view(), name='dashboard'),
    path('categories/', TrainingCategoryListView.as_view(), name='category_list'),
    path('categories/create/', TrainingCategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', TrainingCategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', TrainingCategoryDeleteView.as_view(), name='category_delete'),

    # cursos
    path('courses/', TrainingCourseListView.as_view(), name='course_list'),
    path('courses/create/', TrainingCourseCreateView.as_view(), name='course_create'),
    path('courses/<int:pk>/', TrainingCourseDetailView.as_view(), name='course_detail'),
    path('courses/<int:pk>/edit/', TrainingCourseUpdateView.as_view(), name='course_update'),
    path('courses/<int:pk>/delete/', TrainingCourseDeleteView.as_view(), name='course_delete'),

    # registros
    path('records/', TrainingRecordListView.as_view(), name='record_list'),
    path('records/export-excel/', exportar_formacion_excel, name='record-export-excel'),
    path('records/create/', TrainingRecordCreateView.as_view(), name='record_create'),
    path('records/<int:pk>/', TrainingRecordDetailView.as_view(), name='record_detail'),
    path('records/<int:pk>/edit/', TrainingRecordUpdateView.as_view(), name='record_update'),
    path('records/<int:pk>/delete/', TrainingRecordDeleteView.as_view(), name='record_delete'),
]