from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse, Http404
from .models import PlanPrevention
from .services import get_plan_estadisticas
from .forms import (
    PoliticaForm, OrganigramaForm, DelegadoPRLForm,
    RecursoPreventivoForm, FuncionesForm, ETTTeletrabajoForm,
)


class PlanPreventionMixin:
    def get_plan(self):
        empresa = getattr(self.request, 'active_company', None)
        if not empresa:
            return None
        plan, _ = PlanPrevention.objects.get_or_create(company=empresa)
        return plan

    def get_object(self, queryset=None):
        plan = self.get_plan()
        if not plan:
            from django.http import Http404
            raise Http404
        return plan


class DashboardView(LoginRequiredMixin, PlanPreventionMixin, TemplateView):
    template_name = 'prevention_plan/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        plan = self.get_plan()

        if not plan and self.request.user.is_superuser:
            plans = PlanPrevention.objects.select_related('company').all()
            ctx['plans'] = plans
            ctx['plan'] = None
            ctx['is_global_view'] = True
        else:
            ctx['plan'] = plan
            if plan:
                ctx['stats'] = get_plan_estadisticas(plan)

        return ctx


class PoliticaUpdateView(LoginRequiredMixin, PlanPreventionMixin, UpdateView):
    form_class = PoliticaForm
    template_name = 'prevention_plan/section_form.html'
    success_url = reverse_lazy('prevention_plan:dashboard')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['section_title'] = 'Politica de Prevencion'
        ctx['section_icon'] = 'document'
        return ctx


class OrganigramaUpdateView(LoginRequiredMixin, PlanPreventionMixin, UpdateView):
    form_class = OrganigramaForm
    template_name = 'prevention_plan/section_form.html'
    success_url = reverse_lazy('prevention_plan:dashboard')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['section_title'] = 'Organigrama'
        ctx['section_icon'] = 'users'
        return ctx


class DelegadoUpdateView(LoginRequiredMixin, PlanPreventionMixin, UpdateView):
    form_class = DelegadoPRLForm
    template_name = 'prevention_plan/section_form.html'
    success_url = reverse_lazy('prevention_plan:dashboard')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['section_title'] = 'Delegado de PRL'
        ctx['section_icon'] = 'shield'
        return ctx


class RecursoUpdateView(LoginRequiredMixin, PlanPreventionMixin, UpdateView):
    form_class = RecursoPreventivoForm
    template_name = 'prevention_plan/section_form.html'
    success_url = reverse_lazy('prevention_plan:dashboard')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['section_title'] = 'Recurso Preventivo'
        ctx['section_icon'] = 'clipboard'
        return ctx


class FuncionesUpdateView(LoginRequiredMixin, PlanPreventionMixin, UpdateView):
    form_class = FuncionesForm
    template_name = 'prevention_plan/section_form.html'
    success_url = reverse_lazy('prevention_plan:dashboard')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['section_title'] = 'Funciones y Responsabilidades'
        ctx['section_icon'] = 'list'
        return ctx


class ETTTeletrabajoUpdateView(LoginRequiredMixin, PlanPreventionMixin, UpdateView):
    form_class = ETTTeletrabajoForm
    template_name = 'prevention_plan/section_form.html'
    success_url = reverse_lazy('prevention_plan:dashboard')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['section_title'] = 'Empresas ETT y Teletrabajo'
        ctx['section_icon'] = 'building'
        return ctx


def download_politica(request, plan_id):
    plan = PlanPrevention.objects.filter(pk=plan_id).first()
    if not plan or not plan.politica:
        raise Http404
    return FileResponse(plan.politica.open('rb'), as_attachment=True, filename=plan.politica.name.split('/')[-1])


def download_organigrama(request, plan_id):
    plan = PlanPrevention.objects.filter(pk=plan_id).first()
    if not plan or not plan.organigrama:
        raise Http404
    return FileResponse(plan.organigrama.open('rb'), as_attachment=True, filename=plan.organigrama.name.split('/')[-1])


def download_doc_delegado(request, plan_id, doc_type):
    plan = PlanPrevention.objects.filter(pk=plan_id).first()
    if not plan:
        raise Http404
    field_map = {
        'designacion': 'doc_designacion_delegado',
        'formacion': 'doc_formacion_delegado',
    }
    field = field_map.get(doc_type)
    if not field:
        raise Http404
    doc = getattr(plan, field, None)
    if not doc:
        raise Http404
    return FileResponse(doc.open('rb'), as_attachment=True, filename=doc.name.split('/')[-1])


def download_doc_recurso(request, plan_id, doc_type):
    plan = PlanPrevention.objects.filter(pk=plan_id).first()
    if not plan:
        raise Http404
    field_map = {
        'designacion': 'doc_designacion_recurso',
        'formacion': 'doc_formacion_recurso',
    }
    field = field_map.get(doc_type)
    if not field:
        raise Http404
    doc = getattr(plan, field, None)
    if not doc:
        raise Http404
    return FileResponse(doc.open('rb'), as_attachment=True, filename=doc.name.split('/')[-1])
