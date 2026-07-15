from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.dashboard.views import DashboardView, DashboardChartDataView
from apps.core.views import busqueda_global

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('api/chart-data/', DashboardChartDataView.as_view(), name='chart-data'),
    path('buscar/', busqueda_global, name='busqueda-global'),
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
    path('datos-empresa/', include('apps.company_data.urls', namespace='company_data')),
    path('emergencias/', include('apps.emergency_measures.urls', namespace='emergency_measures')),
    path('quimicos/', include('apps.chemical_products.urls', namespace='chemical_products')),
    path('vigilancia-salud/', include('apps.health_surveillance.urls', namespace='health_surveillance')),
    path('instrucciones-trabajo/', include('apps.work_instructions.urls', namespace='work_instructions')),
    path('auditorias/', include('apps.audits.urls', namespace='audits')),
    path('requisitos-legales/', include('apps.legal_requirements.urls', namespace='legal_requirements')),
    path('autorizaciones/', include('apps.authorizations.urls', namespace='authorizations')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)