from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import CompanyScopedMixin
from .models import MedidaEmergencia, HistorialSimulacro
from .forms import MedidaEmergenciaForm, HistorialSimulacroForm


class MedidaEmergenciaListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = MedidaEmergencia
    template_name = 'emergency_measures/list.html'
    context_object_name = 'medidas'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        empresa = self.get_active_company()
        if empresa:
            qs = qs.filter(company=empresa)
        else:
            qs = qs.none()
        tipo = self.request.GET.get('tipo')
        if tipo:
            qs = qs.filter(tipo=tipo)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        empresa = self.get_active_company()
        if empresa:
            qs = MedidaEmergencia.objects.filter(company=empresa)
            ctx['total'] = qs.count()
            ctx['total_extintores'] = qs.filter(tipo='extintor').count()
            ctx['total_simulacros'] = qs.filter(tipo='simulacro').count()
        else:
            ctx['total'] = 0
            ctx['total_extintores'] = 0
            ctx['total_simulacros'] = 0
        ctx['tipo_filtro'] = self.request.GET.get('tipo', '')
        return ctx


class MedidaEmergenciaCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = MedidaEmergencia
    form_class = MedidaEmergenciaForm
    template_name = 'emergency_measures/form.html'
    success_url = reverse_lazy('emergency_measures:list')

    def form_valid(self, form):
        form.instance.company = self.get_active_company()
        return super().form_valid(form)


class MedidaEmergenciaUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = MedidaEmergencia
    form_class = MedidaEmergenciaForm
    template_name = 'emergency_measures/form.html'
    success_url = reverse_lazy('emergency_measures:list')


class MedidaEmergenciaDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = MedidaEmergencia
    template_name = 'emergency_measures/confirm_delete.html'
    success_url = reverse_lazy('emergency_measures:list')


class MedidaEmergenciaDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = MedidaEmergencia
    template_name = 'emergency_measures/detail.html'
    context_object_name = 'medida'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['historial'] = self.object.historial.all()[:10]
        ctx['form_historial'] = HistorialSimulacroForm(initial={'medida': self.object})
        return ctx


class HistorialSimulacroCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = HistorialSimulacro
    form_class = HistorialSimulacroForm
    template_name = 'emergency_measures/historial_form.html'

    def get_success_url(self):
        return reverse_lazy('emergency_measures:detail', kwargs={'pk': self.object.medida_id})

    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        return super().form_valid(form)
