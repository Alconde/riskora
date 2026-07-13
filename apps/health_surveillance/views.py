from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import CompanyScopedMixin
from .models import ReconocimientoMedico, ControlSalud
from .forms import ReconocimientoMedicoForm, ControlSaludForm


class ReconocimientoMedicoListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = ReconocimientoMedico
    template_name = 'health_surveillance/list.html'
    context_object_name = 'reconocimientos'
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
        apto = self.request.GET.get('apto')
        if apto == 'si':
            qs = qs.filter(apto=True)
        elif apto == 'no':
            qs = qs.filter(apto=False)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        empresa = self.get_active_company()
        if empresa:
            qs = ReconocimientoMedico.objects.filter(company=empresa)
            ctx['total'] = qs.count()
            ctx['apto'] = qs.filter(apto=True).count()
            ctx['no_apto'] = qs.filter(apto=False).count()
            from django.utils import timezone
            ctx['pendientes'] = qs.filter(proximo_reconocimiento__lte=timezone.now().date(), proximo_reconocimiento__gte=timezone.now().date()).count()
        else:
            ctx['total'] = 0
            ctx['apto'] = 0
            ctx['no_apto'] = 0
            ctx['pendientes'] = 0
        ctx['tipo_filtro'] = self.request.GET.get('tipo', '')
        ctx['apto_filtro'] = self.request.GET.get('apto', '')
        return ctx


class ReconocimientoMedicoCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = ReconocimientoMedico
    form_class = ReconocimientoMedicoForm
    template_name = 'health_surveillance/form.html'
    success_url = reverse_lazy('health_surveillance:list')

    def form_valid(self, form):
        form.instance.company = self.get_active_company()
        return super().form_valid(form)


class ReconocimientoMedicoUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = ReconocimientoMedico
    form_class = ReconocimientoMedicoForm
    template_name = 'health_surveillance/form.html'
    success_url = reverse_lazy('health_surveillance:list')


class ReconocimientoMedicoDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = ReconocimientoMedico
    template_name = 'health_surveillance/confirm_delete.html'
    success_url = reverse_lazy('health_surveillance:list')


class ReconocimientoMedicoDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = ReconocimientoMedico
    template_name = 'health_surveillance/detail.html'
    context_object_name = 'reconocimiento'


class ControlSaludListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = ControlSalud
    template_name = 'health_surveillance/controles_list.html'
    context_object_name = 'controles'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        empresa = self.get_active_company()
        if empresa:
            qs = qs.filter(company=empresa)
        else:
            qs = qs.none()
        return qs


class ControlSaludCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = ControlSalud
    form_class = ControlSaludForm
    template_name = 'health_surveillance/control_form.html'
    success_url = reverse_lazy('health_surveillance:controles')

    def form_valid(self, form):
        form.instance.company = self.get_active_company()
        return super().form_valid(form)


class ControlSaludDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = ControlSalud
    template_name = 'health_surveillance/control_confirm_delete.html'
    success_url = reverse_lazy('health_surveillance:controles')
