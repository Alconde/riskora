from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.dashboard.views import DashboardView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('admin/', admin.site.urls),
    path('', include('apps.accounts.urls', namespace='accounts')),
    path('empresas/', include('apps.companies.urls', namespace='companies')),
    path('centros/', include('apps.workcenters.urls', namespace='workcenters')),
    path('trabajadores/', include('apps.workers.urls', namespace='workers')),
    path('training/', include('apps.training.urls')),
    path('documents/', include('apps.documents.urls', namespace='documents')),
    path('', include('apps.tasks.urls', namespace='tasks')),
    path('evaluaciones/', include('apps.risk_assessment.urls', namespace='risk_assessment')),
    path('nc/', include('apps.corrective_actions.urls', namespace='corrective_actions')),
    path('inspecciones/', include('apps.inspections.urls', namespace='inspecciones')),
    path('seguridad/', include('apps.incidents.urls', namespace='incidents')),
    path('eepp/', include('apps.epps.urls', namespace='epps')),
    path('epis/', include('apps.epis.urls', namespace='epis')),
    path('equipos/', include('apps.work_equipment.urls', namespace='work_equipment')),
    path('planificacion/', include('apps.preventive_planning.urls', namespace='preventive_planning')),
    path('plan-prevencion/', include('apps.prevention_plan.urls', namespace='prevention_plan')),
    path('cae/', include('apps.cae.urls', namespace='cae')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)