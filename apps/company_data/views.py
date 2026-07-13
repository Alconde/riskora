from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import CompanyScopedMixin
from apps.workcenters.models import WorkCenter
from apps.workers.models import Worker, JobPosition
from apps.work_equipment.models import EquipoTrabajo


class CompanyDataDashboardView(LoginRequiredMixin, CompanyScopedMixin, TemplateView):
    template_name = 'company_data/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        empresa = self.get_active_company()
        if empresa:
            ctx['total_centros'] = WorkCenter.objects.filter(company=empresa).count()
            ctx['total_trabajadores'] = Worker.objects.filter(company=empresa).count()
            ctx['total_puestos'] = JobPosition.objects.filter(company=empresa).count()
            ctx['total_equipos'] = EquipoTrabajo.objects.filter(empresa=empresa).count()
        else:
            ctx['total_centros'] = 0
            ctx['total_trabajadores'] = 0
            ctx['total_puestos'] = 0
            ctx['total_equipos'] = 0
        return ctx
