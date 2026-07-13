from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.db.models import Q
from django.db import models

from apps.core.mixins import CompanyScopedMixin
from .models import TipoEquipo, EquipoTrabajo, RevisionEquipo, MantenimientoEquipo
from .forms import (
    TipoEquipoForm, EquipoTrabajoForm, RevisionEquipoForm, MantenimientoEquipoForm,
)
from .services import calcular_estadisticas_equipos


# =========================================================
# DASHBOARD
# =========================================================


class WorkEquipmentDashboardView(LoginRequiredMixin, CompanyScopedMixin, TemplateView):
    template_name = 'work_equipment/dashboard.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = self.get_active_company()
        stats = calcular_estadisticas_equipos(empresa)
        context['stats'] = stats

        if empresa:
            context['ultimos_equipos'] = EquipoTrabajo.objects.filter(
                empresa=empresa
            ).select_related('tipo')[:5]
            context['revisiones_pendientes_list'] = [
                eq for eq in EquipoTrabajo.objects.filter(
                    empresa=empresa, activo=True
                ).select_related('tipo')
                if eq.revision_pendiente
            ][:5]

        return context


# =========================================================
# TIPOS DE EQUIPO
# =========================================================


class TipoEquipoListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = TipoEquipo
    template_name = 'work_equipment/tipo_list.html'
    context_object_name = 'tipos'
    paginate_by = 20
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_queryset(self):
        empresa = self.get_active_company()
        queryset = TipoEquipo.objects.filter(
            Q(empresa=empresa) | Q(empresa__isnull=True)
        ) if empresa else TipoEquipo.objects.filter(empresa__isnull=True)

        q = self.request.GET.get('q', '').strip()
        categoria = self.request.GET.get('categoria', '').strip()

        if q:
            queryset = queryset.filter(nombre__icontains=q)
        if categoria:
            queryset = queryset.filter(categoria=categoria)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters'] = self.request.GET
        context['categoria_choices'] = TipoEquipo.Categoria.choices
        return context


class TipoEquipoCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = TipoEquipo
    form_class = TipoEquipoForm
    template_name = 'work_equipment/tipo_form.html'
    success_url = reverse_lazy('work_equipment:tipo-list')
    login_url = '/login/'
    company_field_name = 'empresa'

    def form_valid(self, form):
        empresa = self.get_active_company()
        if empresa:
            form.instance.empresa = empresa
        return super().form_valid(form)


class TipoEquipoUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = TipoEquipo
    form_class = TipoEquipoForm
    template_name = 'work_equipment/tipo_form.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_success_url(self):
        return reverse_lazy('work_equipment:tipo-list')


class TipoEquipoDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = TipoEquipo
    template_name = 'work_equipment/tipo_confirm_delete.html'
    success_url = reverse_lazy('work_equipment:tipo-list')
    login_url = '/login/'
    company_field_name = 'empresa'


# =========================================================
# INVENTARIO DE EQUIPOS
# =========================================================


class EquipoTrabajoListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = EquipoTrabajo
    template_name = 'work_equipment/equipo_list.html'
    context_object_name = 'equipos'
    paginate_by = 20
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_queryset(self):
        queryset = EquipoTrabajo.objects.select_related('empresa', 'tipo')
        queryset = self.get_company_scoped_queryset(queryset)

        q = self.request.GET.get('q', '').strip()
        estado = self.request.GET.get('estado', '').strip()
        tipo = self.request.GET.get('tipo', '').strip()

        if q:
            queryset = queryset.filter(
                Q(nombre__icontains=q) |
                Q(marca__icontains=q) |
                Q(modelo__icontains=q) |
                Q(numero_serie__icontains=q)
            )
        if estado:
            queryset = queryset.filter(estado=estado)
        if tipo:
            queryset = queryset.filter(tipo_id=tipo)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters'] = self.request.GET
        context['estado_choices'] = EquipoTrabajo.Estado.choices
        empresa = self.get_active_company()
        if empresa:
            context['tipos'] = TipoEquipo.objects.filter(
                Q(empresa=empresa) | Q(empresa__isnull=True), activo=True
            )
        else:
            context['tipos'] = TipoEquipo.objects.filter(empresa__isnull=True, activo=True)
        context['stats'] = calcular_estadisticas_equipos(empresa)
        return context


class EquipoTrabajoDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = EquipoTrabajo
    template_name = 'work_equipment/equipo_detail.html'
    context_object_name = 'equipo'
    login_url = '/login/'
    company_field_name = 'empresa'


class EquipoTrabajoCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = EquipoTrabajo
    form_class = EquipoTrabajoForm
    template_name = 'work_equipment/equipo_form.html'
    success_url = reverse_lazy('work_equipment:equipo-list')
    login_url = '/login/'
    company_field_name = 'empresa'

    def form_valid(self, form):
        empresa = self.get_active_company()
        if empresa:
            form.instance.empresa = empresa
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.get_active_company()
        return kwargs


class EquipoTrabajoUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = EquipoTrabajo
    form_class = EquipoTrabajoForm
    template_name = 'work_equipment/equipo_form.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_success_url(self):
        return reverse_lazy('work_equipment:equipo-detail', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.get_active_company()
        return kwargs


class EquipoTrabajoDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = EquipoTrabajo
    template_name = 'work_equipment/equipo_confirm_delete.html'
    success_url = reverse_lazy('work_equipment:equipo-list')
    login_url = '/login/'
    company_field_name = 'empresa'


# =========================================================
# REVISIONES
# =========================================================


class RevisionEquipoListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = RevisionEquipo
    template_name = 'work_equipment/revision_list.html'
    context_object_name = 'revisiones'
    paginate_by = 20
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_queryset(self):
        queryset = RevisionEquipo.objects.select_related(
            'empresa', 'equipo', 'equipo__tipo', 'realizado_por',
        )
        queryset = self.get_company_scoped_queryset(queryset)

        q = self.request.GET.get('q', '').strip()
        resultado = self.request.GET.get('resultado', '').strip()

        if q:
            queryset = queryset.filter(
                Q(equipo__nombre__icontains=q) |
                Q(equipo__marca__icontains=q) |
                Q(observaciones__icontains=q)
            )
        if resultado:
            queryset = queryset.filter(resultado=resultado)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters'] = self.request.GET
        context['resultado_choices'] = RevisionEquipo.Resultado.choices
        return context


class RevisionEquipoCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = RevisionEquipo
    form_class = RevisionEquipoForm
    template_name = 'work_equipment/revision_form.html'
    success_url = reverse_lazy('work_equipment:revision-list')
    login_url = '/login/'
    company_field_name = 'empresa'

    def form_valid(self, form):
        empresa = self.get_active_company()
        if empresa:
            form.instance.empresa = empresa
        form.instance.realizado_por = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.get_active_company()
        return kwargs


class RevisionEquipoUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = RevisionEquipo
    form_class = RevisionEquipoForm
    template_name = 'work_equipment/revision_form.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_success_url(self):
        return reverse_lazy('work_equipment:revision-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.get_active_company()
        return kwargs


class RevisionEquipoDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = RevisionEquipo
    template_name = 'work_equipment/revision_confirm_delete.html'
    success_url = reverse_lazy('work_equipment:revision-list')
    login_url = '/login/'
    company_field_name = 'empresa'


# =========================================================
# MANTENIMIENTOS
# =========================================================


class MantenimientoEquipoListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = MantenimientoEquipo
    template_name = 'work_equipment/mantenimiento_list.html'
    context_object_name = 'mantenimientos'
    paginate_by = 20
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_queryset(self):
        queryset = MantenimientoEquipo.objects.select_related(
            'empresa', 'equipo', 'equipo__tipo', 'realizado_por',
        )
        queryset = self.get_company_scoped_queryset(queryset)

        q = self.request.GET.get('q', '').strip()
        tipo = self.request.GET.get('tipo', '').strip()

        if q:
            queryset = queryset.filter(
                Q(equipo__nombre__icontains=q) |
                Q(equipo__marca__icontains=q) |
                Q(descripcion__icontains=q) |
                Q(proveedor__icontains=q)
            )
        if tipo:
            queryset = queryset.filter(tipo=tipo)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters'] = self.request.GET
        context['tipo_choices'] = MantenimientoEquipo.TipoMantenimiento.choices
        return context


class MantenimientoEquipoCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = MantenimientoEquipo
    form_class = MantenimientoEquipoForm
    template_name = 'work_equipment/mantenimiento_form.html'
    success_url = reverse_lazy('work_equipment:mantenimiento-list')
    login_url = '/login/'
    company_field_name = 'empresa'

    def form_valid(self, form):
        empresa = self.get_active_company()
        if empresa:
            form.instance.empresa = empresa
        form.instance.realizado_por = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.get_active_company()
        return kwargs


class MantenimientoEquipoUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = MantenimientoEquipo
    form_class = MantenimientoEquipoForm
    template_name = 'work_equipment/mantenimiento_form.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_success_url(self):
        return reverse_lazy('work_equipment:mantenimiento-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.get_active_company()
        return kwargs


class MantenimientoEquipoDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = MantenimientoEquipo
    template_name = 'work_equipment/mantenimiento_confirm_delete.html'
    success_url = reverse_lazy('work_equipment:mantenimiento-list')
    login_url = '/login/'
    company_field_name = 'empresa'
