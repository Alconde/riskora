from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from apps.core.mixins import CompanyScopedMixin
from .forms import (
    AuditoriaInternaForm,
    ChecklistAuditoriaForm,
    ChecklistBulkForm,
    InformeAuditoriaForm,
    ProgramaAuditoriaForm,
)
from .models import (
    AuditoriaInterna,
    ChecklistAuditoria,
    InformeAuditoria,
    ProgramaAuditoria,
)
from .services import (
    get_auditorias_pendientes,
    get_dashboard_auditorias,
    get_programa_resumen,
    get_resumen_checklist,
)


# ── Dashboard de auditorías ──────────────────────────────────────────────────

class AuditoriasDashboardView(LoginRequiredMixin, CompanyScopedMixin, TemplateView):
    template_name = 'audits/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        empresa = self.get_active_company()
        ctx['dashboard'] = get_dashboard_auditorias(empresa)
        ctx['programas_recientes'] = ProgramaAuditoria.objects.filter(
            empresa=empresa,
        )[:5]
        return ctx


# ── Programa de Auditorías ───────────────────────────────────────────────────

class ProgramaAuditoriaListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = ProgramaAuditoria
    template_name = 'audits/programa_list.html'
    context_object_name = 'programas'
    paginate_by = 10

    def get_queryset(self):
        return ProgramaAuditoria.objects.filter(
            empresa=self.get_active_company(),
        ).select_related('aprobado_por')


class ProgramaAuditoriaDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = ProgramaAuditoria
    template_name = 'audits/programa_detail.html'
    context_object_name = 'programa'

    def get_queryset(self):
        return ProgramaAuditoria.objects.filter(
            empresa=self.get_active_company(),
        ).select_related('aprobado_por')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['resumen'] = get_programa_resumen(self.object)
        ctx['auditorias'] = self.object.auditorias.select_related('lider_auditoria')
        return ctx


class ProgramaAuditoriaCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = ProgramaAuditoria
    form_class = ProgramaAuditoriaForm
    template_name = 'audits/programa_form.html'
    success_url = reverse_lazy('audits:programa_list')

    def form_valid(self, form):
        form.instance.empresa = self.get_active_company()
        messages.success(self.request, 'Programa de auditorías creado correctamente.')
        return super().form_valid(form)


class ProgramaAuditoriaUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = ProgramaAuditoria
    form_class = ProgramaAuditoriaForm
    template_name = 'audits/programa_form.html'

    def get_queryset(self):
        return ProgramaAuditoria.objects.filter(empresa=self.get_active_company())

    def get_success_url(self):
        return reverse('audits:programa_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Programa actualizado.')
        return super().form_valid(form)


class ProgramaAuditoriaDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = ProgramaAuditoria
    template_name = 'audits/programa_confirm_delete.html'
    success_url = reverse_lazy('audits:programa_list')

    def get_queryset(self):
        return ProgramaAuditoria.objects.filter(empresa=self.get_active_company())

    def form_valid(self, request, *args, **kwargs):
        messages.success(self.request, 'Programa eliminado.')
        return super().form_valid(request, *args, **kwargs)


# ── Auditoría Interna ────────────────────────────────────────────────────────

class AuditoriaInternaListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = AuditoriaInterna
    template_name = 'audits/auditoria_list.html'
    context_object_name = 'auditorias'
    paginate_by = 15

    def get_queryset(self):
        qs = AuditoriaInterna.objects.filter(
            empresa=self.get_active_company(),
        ).select_related('programa', 'lider_auditoria')
        estado = self.request.GET.get('estado')
        if estado:
            qs = qs.filter(estado=estado)
        return qs


class AuditoriaInternaDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = AuditoriaInterna
    template_name = 'audits/auditoria_detail.html'
    context_object_name = 'auditoria'

    def get_queryset(self):
        return AuditoriaInterna.objects.filter(
            empresa=self.get_active_company(),
        ).select_related('programa', 'lider_auditoria')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['resumen'] = get_resumen_checklist(self.object)
        ctx['checklist'] = self.object.checklist.select_related(
            'accion_correctiva',
            'responsable_seguimiento',
        )
        ctx['tiene_informe'] = self.object.tiene_informe
        ctx['InformeAuditoria'] = InformeAuditoria
        return ctx


class AuditoriaInternaCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = AuditoriaInterna
    form_class = AuditoriaInternaForm
    template_name = 'audits/auditoria_form.html'

    def form_valid(self, form):
        form.instance.empresa = self.get_active_company()
        messages.success(self.request, 'Auditoría interna creada.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('audits:auditoria_detail', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        empresa = self.get_active_company()
        kwargs['queryset'] = {
            'programa': ProgramaAuditoria.objects.filter(empresa=empresa),
        }
        return kwargs


class AuditoriaInternaUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = AuditoriaInterna
    form_class = AuditoriaInternaForm
    template_name = 'audits/auditoria_form.html'

    def get_queryset(self):
        return AuditoriaInterna.objects.filter(empresa=self.get_active_company())

    def get_success_url(self):
        return reverse('audits:auditoria_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Auditoría actualizada.')
        return super().form_valid(form)


class AuditoriaInternaDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = AuditoriaInterna
    template_name = 'audits/auditoria_confirm_delete.html'

    def get_queryset(self):
        return AuditoriaInterna.objects.filter(empresa=self.get_active_company())

    def get_success_url(self):
        return reverse('audits:programa_detail', kwargs={'pk': self.object.programa_id})

    def form_valid(self, request, *args, **kwargs):
        messages.success(self.request, 'Auditoría eliminada.')
        return super().form_valid(request, *args, **kwargs)


# ── Checklist ────────────────────────────────────────────────────────────────

class ChecklistCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = ChecklistAuditoria
    form_class = ChecklistAuditoriaForm
    template_name = 'audits/checklist_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['auditoria'] = get_object_or_404(
            AuditoriaInterna,
            pk=self.kwargs['auditoria_pk'],
            empresa=self.get_active_company(),
        )
        return ctx

    def form_valid(self, form):
        form.instance.auditoria = get_object_or_404(
            AuditoriaInterna,
            pk=self.kwargs['auditoria_pk'],
            empresa=self.get_active_company(),
        )
        messages.success(self.request, 'Item de checklist añadido.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('audits:auditoria_detail', kwargs={'pk': self.kwargs['auditoria_pk']})


class ChecklistBulkCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = ChecklistAuditoria
    form_class = ChecklistBulkForm
    template_name = 'audits/checklist_bulk_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        auditoria = get_object_or_404(
            AuditoriaInterna,
            pk=self.kwargs['auditoria_pk'],
            empresa=self.get_active_company(),
        )
        ctx['auditoria'] = auditoria
        ctx['form'] = ChecklistBulkForm(empresa=self.get_active_company())
        return ctx

    def form_valid(self, form):
        auditoria = get_object_or_404(
            AuditoriaInterna,
            pk=self.kwargs['auditoria_pk'],
            empresa=self.get_active_company(),
        )
        from .services import CHECKLIST_ISO_45001
        seleccionados = form.cleaned_data['clausulas']
        plantilla_map = {str(item['id']): item for item in CHECKLIST_ISO_45001}

        items_creados = 0
        for item_id in seleccionados:
            item = plantilla_map.get(str(item_id))
            if item:
                ChecklistAuditoria.objects.create(
                    auditoria=auditoria,
                    clausula_iso=item['clausula'],
                    seccion=item['seccion'],
                    requisito=item['requisito'],
                    evidencia_requerida=item['evidencia_requerida'],
                )
                items_creados += 1

        messages.success(
            self.request,
            f'Se crearon {items_creados} items de checklist desde la plantilla ISO 45001.',
        )
        return redirect('audits:auditoria_detail', pk=auditoria.pk)

    def get_success_url(self):
        return reverse('audits:auditoria_detail', kwargs={'pk': self.kwargs['auditoria_pk']})


class ChecklistUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = ChecklistAuditoria
    form_class = ChecklistAuditoriaForm
    template_name = 'audits/checklist_form.html'

    def get_queryset(self):
        return ChecklistAuditoria.objects.filter(
            auditoria__empresa=self.get_active_company(),
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['auditoria'] = self.object.auditoria
        return ctx

    def get_success_url(self):
        return reverse('audits:auditoria_detail', kwargs={'pk': self.object.auditoria_id})


# ── Informe ──────────────────────────────────────────────────────────────────

class InformeAuditoriaCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = InformeAuditoria
    form_class = InformeAuditoriaForm
    template_name = 'audits/informe_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        auditoria = get_object_or_404(
            AuditoriaInterna,
            pk=self.kwargs['auditoria_pk'],
            empresa=self.get_active_company(),
        )
        ctx['auditoria'] = auditoria
        return ctx

    def form_valid(self, form):
        auditoria = get_object_or_404(
            AuditoriaInterna,
            pk=self.kwargs['auditoria_pk'],
            empresa=self.get_active_company(),
        )
        form.instance.auditoria = auditoria
        auditoria.estado = 'cerrada'
        auditoria.save(update_fields=['estado'])
        messages.success(self.request, 'Informe de auditoría creado y auditoría cerrada.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('audits:auditoria_detail', kwargs={'pk': self.kwargs['auditoria_pk']})


class InformeAuditoriaDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = InformeAuditoria
    template_name = 'audits/informe_detail.html'
    context_object_name = 'informe'

    def get_queryset(self):
        return InformeAuditoria.objects.filter(
            auditoria__empresa=self.get_active_company(),
        ).select_related('auditoria', 'elaborado_por', 'aprobado_por')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['resumen'] = get_resumen_checklist(self.object.auditoria)
        return ctx


class InformeAuditoriaUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = InformeAuditoria
    form_class = InformeAuditoriaForm
    template_name = 'audits/informe_form.html'

    def get_queryset(self):
        return InformeAuditoria.objects.filter(
            auditoria__empresa=self.get_active_company(),
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['auditoria'] = self.object.auditoria
        return ctx

    def get_success_url(self):
        return reverse('audits:informe_detail', kwargs={'pk': self.object.pk})
