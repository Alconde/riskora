import json
from datetime import timedelta
from calendar import month_name

from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.utils import timezone
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth

from apps.core.mixins import CompanyScopedMixin
from apps.dashboard.services import build_dashboard_context


class DashboardView(LoginRequiredMixin, CompanyScopedMixin, TemplateView):
    template_name = 'dashboard/home.html'
    login_url = '/login/'
    company_field_name = 'company'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_company = self.get_active_company()
        is_superuser = self.request.user.is_superuser

        context.update(
            build_dashboard_context(
                active_company=active_company,
                is_superuser=is_superuser
            )
        )
        return context


class DashboardChartDataView(LoginRequiredMixin, CompanyScopedMixin, TemplateView):
    """Devuelve datos JSON para las gráficas del dashboard."""
    login_url = '/login/'
    company_field_name = 'company'

    def get(self, request, *args, **kwargs):
        empresa = self.get_active_company()
        hoy = timezone.localdate()
        hace_12_meses = hoy - timedelta(days=365)

        data = {}

        # 1. Accidentes por mes (últimos 12 meses)
        from apps.incidents.models import Accidente
        qs_acc = Accidente.objects.filter(fecha__date__gte=hace_12_meses)
        if empresa:
            qs_acc = qs_acc.filter(empresa=empresa)
        acc_por_mes = (
            qs_acc
            .annotate(mes=TruncMonth('fecha'))
            .values('mes')
            .annotate(total=Count('id'))
            .order_by('mes')
        )
        data['accidentes'] = {
            'labels': [d['mes'].strftime('%b %Y') for d in acc_por_mes],
            'values': [d['total'] for d in acc_por_mes],
        }

        # 2. Formación por estado
        from apps.training.models import TrainingRecord
        qs_tr = TrainingRecord.objects.all()
        if empresa:
            qs_tr = qs_tr.filter(company=empresa)
        form_estado = (
            qs_tr
            .values('status')
            .annotate(total=Count('id'))
            .order_by('status')
        )
        status_labels = dict(TrainingRecord.Status.choices)
        data['formacion'] = {
            'labels': [status_labels.get(d['status'], d['status']) for d in form_estado],
            'values': [d['total'] for d in form_estado],
        }

        # 3. Tareas por prioridad
        from apps.tasks.models import Task
        qs_task = Task.objects.all()
        if empresa:
            qs_task = qs_task.filter(company=empresa)
        task_prio = (
            qs_task
            .values('priority')
            .annotate(total=Count('id'))
            .order_by('priority')
        )
        prio_labels = dict(Task.Priority.choices) if hasattr(Task, 'Priority') else {}
        data['tareas'] = {
            'labels': [prio_labels.get(d['priority'], d['priority']) for d in task_prio],
            'values': [d['total'] for d in task_prio],
        }

        # 4. No conformidades por fuente
        from apps.corrective_actions.models import NoConformidad
        qs_nc = NoConformidad.objects.all()
        if empresa:
            qs_nc = qs_nc.filter(empresa=empresa)
        nc_fuente = (
            qs_nc
            .values('fuente')
            .annotate(total=Count('id'))
            .order_by('fuente')
        )
        fuente_labels = dict(NoConformidad.Fuente.choices)
        data['no_conformidades'] = {
            'labels': [fuente_labels.get(d['fuente'], d['fuente']) for d in nc_fuente],
            'values': [d['total'] for d in nc_fuente],
        }

        return JsonResponse(data)