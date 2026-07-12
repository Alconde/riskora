from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.dashboard.views import DashboardView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('admin/', admin.site.urls),
    path('empresas/', include('apps.companies.urls')),
    path('centros/', include('apps.workcenters.urls')),
    path('trabajadores/', include('apps.workers.urls')),
    path('training/', include('apps.training.urls')),
    path('documents/', include('apps.documents.urls', namespace='documents')),
    path('', include('apps.tasks.urls', namespace='tasks')),
    path('evaluaciones/', include('apps.risk_assessment.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)