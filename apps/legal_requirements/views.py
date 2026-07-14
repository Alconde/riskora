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
    AlertaLegalForm,
    CumplimientoBulkForm,
    CumplimientoLegalForm,
    NormativaLegalForm,
    RequisitoLegalForm,
)
from .models import (
    AlertaLegal,
    CumplimientoLegal,
    NormativaLegal,
    RequisitoLegal,
)
from .services import (
    get_alertas_legales,
    get_cumplimiento_empresa,
    get_cumplimientos_proximos,
    get_cumplimientos_vencidos,
)


# ── Dashboard ────────────────────────────────────────────────────────────────

class LegalDashboardView(LoginRequiredMixin, CompanyScopedMixin, TemplateView):
    template_name = 'legal_requirements/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        empresa = self.get_active_company()
        ctx['resumen'] = get_cumplimiento_empresa(empresa)
        ctx['alertas'] = get_alertas_legales(empresa)[:10]
        ctx['alertas_count'] = get_alertas_legales(empresa).count()
        ctx['vencidos'] = get_cumplimientos_vencidos(empresa)[:5]
        ctx['vencidos_count'] = get_cumplimientos_vencidos(empresa).count()
        ctx['proximos'] = get_cumplimientos_proximos(empresa)[:5]
        return ctx


# ── Alertas ──────────────────────────────────────────────────────────────────

class AlertaLegalListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = AlertaLegal
    template_name = 'legal_requirements/alerta_list.html'
    context_object_name = 'alertas'
    paginate_by = 20

    def get_queryset(self):
        return AlertaLegal.objects.filter(
            empresa=self.get_active_company(),
        ).select_related('cumplimiento', 'normativa')


class AlertaLegalMarcarLeidaView(LoginRequiredMixin, CompanyScopedMixin, TemplateView):
    def get(self, request, pk):
        alerta = get_object_or_404(
            AlertaLegal, pk=pk, empresa=self.get_active_company(),
        )
        alerta.leida = True
        alerta.save(update_fields=['leida'])
        messages.success(request, 'Alerta marcada como leída.')
        return redirect('legal_requirements:alerta_list')


class AlertaLegalResolverView(LoginRequiredMixin, CompanyScopedMixin, TemplateView):
    def get(self, request, pk):
        alerta = get_object_or_404(
            AlertaLegal, pk=pk, empresa=self.get_active_company(),
        )
        alerta.resuelta = True
        alerta.leida = True
        alerta.save(update_fields=['resuelta', 'leida'])
        messages.success(request, 'Alerta marcada como resuelta.')
        return redirect('legal_requirements:alerta_list')


# ── Normativa Legal ──────────────────────────────────────────────────────────

class NormativaLegalListView(LoginRequiredMixin, ListView):
    model = NormativaLegal
    template_name = 'legal_requirements/normativa_list.html'
    context_object_name = 'normativas'
    paginate_by = 20

    def get_queryset(self):
        qs = NormativaLegal.objects.all()
        tipo = self.request.GET.get('tipo')
        ambito = self.request.GET.get('ambito')
        activa = self.request.GET.get('activa')
        if tipo:
            qs = qs.filter(tipo=tipo)
        if ambito:
            qs = qs.filter(ambito=ambito)
        if activa == '0':
            qs = qs.filter(activa=False)
        elif activa == '1':
            qs = qs.filter(activa=True)
        return qs


class NormativaLegalDetailView(LoginRequiredMixin, DetailView):
    model = NormativaLegal
    template_name = 'legal_requirements/normativa_detail.html'
    context_object_name = 'normativa'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['requisitos'] = self.object.requisitos.all()
        return ctx


class NormativaLegalCreateView(LoginRequiredMixin, CreateView):
    model = NormativaLegal
    form_class = NormativaLegalForm
    template_name = 'legal_requirements/normativa_form.html'
    success_url = reverse_lazy('legal_requirements:normativa_list')

    def form_valid(self, form):
        messages.success(self.request, 'Normativa creada correctamente.')
        return super().form_valid(form)


class NormativaLegalUpdateView(LoginRequiredMixin, UpdateView):
    model = NormativaLegal
    form_class = NormativaLegalForm
    template_name = 'legal_requirements/normativa_form.html'
    success_url = reverse_lazy('legal_requirements:normativa_list')

    def form_valid(self, form):
        messages.success(self.request, 'Normativa actualizada.')
        return super().form_valid(form)


class NormativaLegalDeleteView(LoginRequiredMixin, DeleteView):
    model = NormativaLegal
    template_name = 'legal_requirements/normativa_confirm_delete.html'
    success_url = reverse_lazy('legal_requirements:normativa_list')

    def form_valid(self, request, *args, **kwargs):
        messages.success(self.request, 'Normativa eliminada.')
        return super().form_valid(request, *args, **kwargs)


# ── Requisitos Legales ───────────────────────────────────────────────────────

class RequisitoLegalListView(LoginRequiredMixin, ListView):
    model = RequisitoLegal
    template_name = 'legal_requirements/requisito_list.html'
    context_object_name = 'requisitos'
    paginate_by = 20

    def get_queryset(self):
        qs = RequisitoLegal.objects.select_related('normativa')
        normativa = self.request.GET.get('normativa')
        categoria = self.request.GET.get('categoria')
        if normativa:
            qs = qs.filter(normativa_id=normativa)
        if categoria:
            qs = qs.filter(categoria=categoria)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['normativas'] = NormativaLegal.objects.filter(activa=True)
        return ctx


class RequisitoLegalCreateView(LoginRequiredMixin, CreateView):
    model = RequisitoLegal
    form_class = RequisitoLegalForm
    template_name = 'legal_requirements/requisito_form.html'
    success_url = reverse_lazy('legal_requirements:requisito_list')

    def form_valid(self, form):
        messages.success(self.request, 'Requisito legal creado.')
        return super().form_valid(form)


class RequisitoLegalUpdateView(LoginRequiredMixin, UpdateView):
    model = RequisitoLegal
    form_class = RequisitoLegalForm
    template_name = 'legal_requirements/requisito_form.html'
    success_url = reverse_lazy('legal_requirements:requisito_list')

    def form_valid(self, form):
        messages.success(self.request, 'Requisito actualizado.')
        return super().form_valid(form)


# ── Cumplimiento Legal ───────────────────────────────────────────────────────

class CumplimientoLegalListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = CumplimientoLegal
    template_name = 'legal_requirements/cumplimiento_list.html'
    context_object_name = 'cumplimientos'
    paginate_by = 20

    def get_queryset(self):
        return CumplimientoLegal.objects.filter(
            empresa=self.get_active_company(),
        ).select_related('requisito', 'requisito__normativa', 'responsable')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['resumen'] = get_cumplimiento_empresa(self.get_active_company())
        return ctx


class CumplimientoLegalCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = CumplimientoLegal
    form_class = CumplimientoLegalForm
    template_name = 'legal_requirements/cumplimiento_form.html'
    success_url = reverse_lazy('legal_requirements:cumplimiento_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.get_active_company()
        return kwargs

    def form_valid(self, form):
        form.instance.empresa = self.get_active_company()
        messages.success(self.request, 'Cumplimiento legal registrado.')
        return super().form_valid(form)


class CumplimientoLegalUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = CumplimientoLegal
    form_class = CumplimientoLegalForm
    template_name = 'legal_requirements/cumplimiento_form.html'
    success_url = reverse_lazy('legal_requirements:cumplimiento_list')

    def get_queryset(self):
        return CumplimientoLegal.objects.filter(empresa=self.get_active_company())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.get_active_company()
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Cumplimiento actualizado.')
        return super().form_valid(form)


class CumplimientoBulkCreateView(LoginRequiredMixin, CompanyScopedMixin, TemplateView):
    template_name = 'legal_requirements/cumplimiento_bulk_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form'] = CumplimientoBulkForm(empresa=self.get_active_company())
        return ctx

    def post(self, request):
        form = CumplimientoBulkForm(request.POST, empresa=self.get_active_company())
        if form.is_valid():
            empresa = self.get_active_company()
            requisitos_ids = form.cleaned_data['normativas']
            from .models import RequisitoLegal
            requisitos = RequisitoLegal.objects.filter(id__in=requisitos_ids)
            count = 0
            for req in requisitos:
                CumplimientoLegal.objects.get_or_create(
                    empresa=empresa,
                    requisito=req,
                    defaults={'estado': 'pendiente'},
                )
                count += 1
            messages.success(
                request,
                f'Se crearon {count} registros de cumplimiento legal.',
            )
            return redirect('legal_requirements:cumplimiento_list')
        ctx = self.get_context_data()
        ctx['form'] = form
        return self.render_to_response(ctx)
