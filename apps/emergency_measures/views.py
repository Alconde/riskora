from django.urls import reverse_lazy
from django.views.generic import (
    TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from apps.core.mixins import CompanyScopedMixin
from apps.workers.models import Worker
from .models import (
    MedioProteccionIncendios, EmpresaMedioProteccion, PlanAutoproteccion,
    EquipoEmergencia, MiembroEquipoEmergencia, RegistroSimulacro,
    EntregaInformacionEmergencia,
)
from .forms import (
    PlanAutoproteccionForm, EmpresaMedioProteccionForm, EquipoEmergenciaForm,
    MiembroEquipoForm, RegistroSimulacroForm, EntregaInformacionForm,
)


class EmergencyDashboardView(LoginRequiredMixin, CompanyScopedMixin, TemplateView):
    template_name = 'emergency_measures/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        empresa = self.get_active_company()
        if empresa:
            ctx['total_medios'] = EmpresaMedioProteccion.objects.filter(company=empresa).count()
            ctx['total_equipos'] = EquipoEmergencia.objects.filter(company=empresa).count()
            ctx['total_simulacros'] = RegistroSimulacro.objects.filter(company=empresa).count()
            ctx['total_entregas'] = EntregaInformacionEmergencia.objects.filter(company=empresa).count()
            ctx['trabajadores'] = Worker.objects.filter(company=empresa).count()
            ctx['entregas_pendientes'] = ctx['trabajadores'] - ctx['total_entregas']
            try:
                plan = PlanAutoproteccion.objects.get(company=empresa)
                ctx['plan'] = plan
            except PlanAutoproteccion.DoesNotExist:
                ctx['plan'] = None
            ctx['equipos'] = EquipoEmergencia.objects.filter(company=empresa)
        return ctx


class PlanAutoproteccionView(LoginRequiredMixin, CompanyScopedMixin, TemplateView):
    template_name = 'emergency_measures/plan_autoproteccion.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        empresa = self.get_active_company()
        if empresa:
            ctx['plan'], _ = PlanAutoproteccion.objects.get_or_create(company=empresa)
            ctx['form'] = PlanAutoproteccionForm(instance=ctx['plan'])
        return ctx

    def post(self, request, *args, **kwargs):
        empresa = self.get_active_company()
        plan, _ = PlanAutoproteccion.objects.get_or_create(company=empresa)
        form = PlanAutoproteccionForm(request.POST, request.FILES, instance=plan)
        if form.is_valid():
            form.save()
            return redirect('emergency_measures:plan-autoproteccion')
        ctx = self.get_context_data(**kwargs)
        ctx['form'] = form
        return self.render_to_response(ctx)


class MediosProteccionView(LoginRequiredMixin, CompanyScopedMixin, TemplateView):
    template_name = 'emergency_measures/medios_proteccion.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        empresa = self.get_active_company()
        if empresa:
            ctx['medios_empresa'] = EmpresaMedioProteccion.objects.filter(company=empresa).select_related('medio')
            ctx['catalogo'] = MedioProteccionIncendios.objects.filter(activo=True)
            seleccionados = set(ctx['medios_empresa'].values_list('medio_id', flat=True))
            ctx['disponibles'] = [m for m in ctx['catalogo'] if m.id not in seleccionados]
            ctx['form'] = EmpresaMedioProteccionForm()
        return ctx

    def post(self, request, *args, **kwargs):
        empresa = self.get_active_company()
        form = EmpresaMedioProteccionForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.company = empresa
            obj.save()
            return redirect('emergency_measures:medios-proteccion')
        ctx = self.get_context_data(**kwargs)
        ctx['form'] = form
        return self.render_to_response(ctx)


class EmpresaMedioProteccionDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = EmpresaMedioProteccion
    template_name = 'emergency_measures/confirm_delete.html'
    success_url = reverse_lazy('emergency_measures:medios-proteccion')


class EmpresaMedioProteccionUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = EmpresaMedioProteccion
    form_class = EmpresaMedioProteccionForm
    template_name = 'emergency_measures/medio_form.html'
    success_url = reverse_lazy('emergency_measures:medios-proteccion')


class EquiposEmergenciaListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = EquipoEmergencia
    template_name = 'emergency_measures/equipos_list.html'
    context_object_name = 'equipos'

    def get_queryset(self):
        qs = super().get_queryset()
        empresa = self.get_active_company()
        if empresa:
            return qs.filter(company=empresa)
        return qs.none()


class EquipoEmergenciaCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = EquipoEmergencia
    form_class = EquipoEmergenciaForm
    template_name = 'emergency_measures/equipo_form.html'
    success_url = reverse_lazy('emergency_measures:equipos')

    def form_valid(self, form):
        form.instance.company = self.get_active_company()
        return super().form_valid(form)


class EquipoEmergenciaUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = EquipoEmergencia
    form_class = EquipoEmergenciaForm
    template_name = 'emergency_measures/equipo_form.html'
    success_url = reverse_lazy('emergency_measures:equipos')


class EquipoEmergenciaDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = EquipoEmergencia
    template_name = 'emergency_measures/confirm_delete.html'
    success_url = reverse_lazy('emergency_measures:equipos')


class EquipoEmergenciaDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = EquipoEmergencia
    template_name = 'emergency_measures/equipo_detail.html'
    context_object_name = 'equipo'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['miembros'] = self.object.miembros.select_related('trabajador')
        empresa = self.get_active_company()
        if empresa:
            miembros_actuales = ctx['miembros'].values_list('trabajador_id', flat=True)
            ctx['trabajadores_disponibles'] = Worker.objects.filter(company=empresa).exclude(id__in=miembros_actuales)
        ctx['form_miembro'] = MiembroEquipoForm()
        return ctx


class MiembroEquipoCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = MiembroEquipoEmergencia
    form_class = MiembroEquipoForm
    template_name = 'emergency_measures/miembro_form.html'

    def get_success_url(self):
        return reverse_lazy('emergency_measures:equipo-detail', kwargs={'pk': self.object.equipo_id})

    def form_valid(self, form):
        form.instance.equipo = EquipoEmergencia.objects.get(pk=self.kwargs['equipo_pk'])
        return super().form_valid(form)


class MiembroEquipoDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = MiembroEquipoEmergencia
    template_name = 'emergency_measures/confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('emergency_measures:equipo-detail', kwargs={'pk': self.object.equipo_id})


class SimulacrosListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = RegistroSimulacro
    template_name = 'emergency_measures/simulacros_list.html'
    context_object_name = 'simulacros'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        empresa = self.get_active_company()
        if empresa:
            return qs.filter(company=empresa)
        return qs.none()


class SimulacroCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = RegistroSimulacro
    form_class = RegistroSimulacroForm
    template_name = 'emergency_measures/simulacro_form.html'
    success_url = reverse_lazy('emergency_measures:simulacros')

    def form_valid(self, form):
        form.instance.company = self.get_active_company()
        form.instance.creado_por = self.request.user
        return super().form_valid(form)


class SimulacroDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = RegistroSimulacro
    template_name = 'emergency_measures/confirm_delete.html'
    success_url = reverse_lazy('emergency_measures:simulacros')


class EntregasInfoListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = EntregaInformacionEmergencia
    template_name = 'emergency_measures/entregas_list.html'
    context_object_name = 'entregas'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        empresa = self.get_active_company()
        if empresa:
            return qs.filter(company=empresa).select_related('trabajador')
        return qs.none()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        empresa = self.get_active_company()
        if empresa:
            ctx['total_workers'] = Worker.objects.filter(company=empresa).count()
            ctx['total_entregas'] = EntregaInformacionEmergencia.objects.filter(company=empresa).count()
        return ctx


class EntregaInfoCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = EntregaInformacionEmergencia
    form_class = EntregaInformacionForm
    template_name = 'emergency_measures/entrega_form.html'
    success_url = reverse_lazy('emergency_measures:entregas-info')

    def form_valid(self, form):
        form.instance.company = self.get_active_company()
        return super().form_valid(form)


class EntregaInfoDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = EntregaInformacionEmergencia
    template_name = 'emergency_measures/confirm_delete.html'
    success_url = reverse_lazy('emergency_measures:entregas-info')
