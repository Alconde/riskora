from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q

from apps.core.mixins import CompanyScopedMixin
from .models import PlantillaInspeccion, PlantillaInspeccionItem, Inspeccion, ItemInspeccion
from .forms import (
    PlantillaInspeccionForm, PlantillaItemForm,
    InspeccionForm, ItemInspeccionForm,
)
from .services import generar_nc_desde_item


# =========================================================
# PLANTILLAS DE INSPECCION
# =========================================================


class PlantillaListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = PlantillaInspeccion
    template_name = 'inspections/plantilla_list.html'
    context_object_name = 'plantillas'
    paginate_by = 20
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_queryset(self):
        queryset = PlantillaInspeccion.objects.select_related('empresa')
        return self.get_company_scoped_queryset(queryset)


class PlantillaCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = PlantillaInspeccion
    form_class = PlantillaInspeccionForm
    template_name = 'inspections/plantilla_form.html'
    success_url = reverse_lazy('inspections:plantilla-list')
    login_url = '/login/'
    company_field_name = 'empresa'

    def form_valid(self, form):
        empresa = self.get_active_company()
        if empresa:
            form.instance.empresa = empresa
        return super().form_valid(form)


class PlantillaUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = PlantillaInspeccion
    form_class = PlantillaInspeccionForm
    template_name = 'inspections/plantilla_form.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_success_url(self):
        return reverse_lazy('inspections:plantilla-detail', kwargs={'pk': self.object.pk})


class PlantillaDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = PlantillaInspeccion
    template_name = 'inspections/plantilla_detail.html'
    context_object_name = 'plantilla'
    login_url = '/login/'
    company_field_name = 'empresa'


class PlantillaDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = PlantillaInspeccion
    template_name = 'inspections/plantilla_confirm_delete.html'
    success_url = reverse_lazy('inspections:plantilla-list')
    login_url = '/login/'
    company_field_name = 'empresa'


class PlantillaItemCreateView(LoginRequiredMixin, CreateView):
    model = PlantillaInspeccionItem
    form_class = PlantillaItemForm
    template_name = 'inspections/plantilla_item_form.html'
    login_url = '/login/'

    def form_valid(self, form):
        plantilla = PlantillaInspeccion.objects.get(pk=self.kwargs['plantilla_pk'])
        form.instance.plantilla = plantilla
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('inspections:plantilla-detail', kwargs={'pk': self.kwargs['plantilla_pk']})


# =========================================================
# INSPECCIONES
# =========================================================


class InspeccionListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = Inspeccion
    template_name = 'inspections/inspeccion_list.html'
    context_object_name = 'inspecciones'
    paginate_by = 20
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_queryset(self):
        queryset = Inspeccion.objects.select_related(
            'empresa', 'plantilla', 'centro_trabajo', 'inspector',
        )
        queryset = self.get_company_scoped_queryset(queryset)

        q = self.request.GET.get('q', '').strip()
        estado = self.request.GET.get('estado', '').strip()
        centro = self.request.GET.get('centro', '').strip()

        if q:
            queryset = queryset.filter(
                Q(centro_trabajo__name__icontains=q) |
                Q(observaciones__icontains=q)
            )
        if estado:
            queryset = queryset.filter(estado=estado)
        if centro:
            queryset = queryset.filter(centro_trabajo_id=centro)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters'] = self.request.GET
        context['estado_choices'] = Inspeccion.Estado.choices
        empresa = self.get_active_company()
        if empresa:
            from apps.workcenters.models import WorkCenter
            context['centros'] = WorkCenter.objects.filter(company=empresa)
        return context


class InspeccionDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = Inspeccion
    template_name = 'inspections/inspeccion_detail.html'
    context_object_name = 'inspeccion'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item_form'] = ItemInspeccionForm()
        return context


class InspeccionCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = Inspeccion
    form_class = InspeccionForm
    template_name = 'inspections/inspeccion_form.html'
    success_url = reverse_lazy('inspections:inspeccion-list')
    login_url = '/login/'
    company_field_name = 'empresa'

    def form_valid(self, form):
        empresa = self.get_active_company()
        if empresa:
            form.instance.empresa = empresa
        form.instance.creado_por = self.request.user
        response = super().form_valid(form)
        plantilla = form.cleaned_data.get('plantilla')
        if plantilla:
            for item in plantilla.items.order_by('orden'):
                ItemInspeccion.objects.create(
                    inspeccion=self.object,
                    orden=item.orden,
                    descripcion=item.descripcion,
                )
        return response


class InspeccionUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = Inspeccion
    form_class = InspeccionForm
    template_name = 'inspections/inspeccion_form.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_success_url(self):
        return reverse_lazy('inspections:inspeccion-detail', kwargs={'pk': self.object.pk})


class InspeccionDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = Inspeccion
    template_name = 'inspections/inspeccion_confirm_delete.html'
    success_url = reverse_lazy('inspections:inspeccion-list')
    login_url = '/login/'
    company_field_name = 'empresa'


class InspeccionItemCreateView(LoginRequiredMixin, CreateView):
    model = ItemInspeccion
    form_class = ItemInspeccionForm
    template_name = 'inspections/inspeccion_item_form.html'
    login_url = '/login/'

    def form_valid(self, form):
        form.instance.inspeccion = Inspeccion.objects.get(pk=self.kwargs['inspeccion_pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('inspections:inspeccion-detail', kwargs={'pk': self.kwargs['inspeccion_pk']})


class InspeccionItemUpdateView(LoginRequiredMixin, UpdateView):
    model = ItemInspeccion
    form_class = ItemInspeccionForm
    template_name = 'inspections/inspeccion_item_form.html'
    login_url = '/login/'

    def get_success_url(self):
        return reverse_lazy('inspections:inspeccion-detail', kwargs={'pk': self.object.inspeccion.pk})


class InspeccionItemDeleteView(LoginRequiredMixin, DeleteView):
    model = ItemInspeccion
    template_name = 'inspections/inspeccion_item_confirm_delete.html'
    login_url = '/login/'

    def get_success_url(self):
        return reverse_lazy('inspections:inspeccion-detail', kwargs={'pk': self.object.inspeccion.pk})


class InspeccionItemNCView(LoginRequiredMixin, CreateView):
    from apps.corrective_actions.models import NoConformidad
    from apps.corrective_actions.forms import NoConformidadForm
    model = NoConformidad
    form_class = NoConformidadForm
    template_name = 'inspections/inspeccion_item_nc.html'
    login_url = '/login/'

    def get_item(self):
        return ItemInspeccion.objects.get(pk=self.kwargs['item_pk'])

    def form_valid(self, form):
        item = self.get_item()
        inspeccion = item.inspeccion
        from apps.corrective_actions.services import generar_codigo_nc
        form.instance.empresa = inspeccion.empresa
        form.instance.codigo = generar_codigo_nc(inspeccion.empresa)
        form.instance.creado_por = self.request.user
        form.instance.fecha_deteccion = inspeccion.fecha_inspeccion
        form.instance.centro_trabajo = inspeccion.centro_trabajo
        form.instance.fuente = 'inspeccion'
        response = super().form_valid(form)
        item.no_conformidad = self.object
        item.save(update_fields=['no_conformidad'])
        return response

    def get_success_url(self):
        item = self.get_item()
        return reverse_lazy('inspections:inspeccion-detail', kwargs={'pk': item.inspeccion.pk})
