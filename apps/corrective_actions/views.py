from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.db.models import Q

from apps.core.mixins import CompanyScopedMixin
from .models import NoConformidad, AccionCorrectiva, AccionPreventiva
from .forms import (
    NoConformidadForm, NoConformidadCerrarForm,
    AccionCorrectivaForm, AccionPreventivaForm,
)
from .services import generar_codigo_nc


# =========================================================
# NO CONFORMIDADES
# =========================================================


class NCListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = NoConformidad
    template_name = 'corrective_actions/nc_list.html'
    context_object_name = 'no_conformidades'
    paginate_by = 20
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_queryset(self):
        queryset = NoConformidad.objects.select_related(
            'empresa', 'detectado_por', 'centro_trabajo', 'trabajador',
        )
        queryset = self.get_company_scoped_queryset(queryset)

        q = self.request.GET.get('q', '').strip()
        estado = self.request.GET.get('estado', '').strip()
        gravedad = self.request.GET.get('gravedad', '').strip()
        fuente = self.request.GET.get('fuente', '').strip()
        vencidas = self.request.GET.get('vencidas', '').strip()

        if q:
            queryset = queryset.filter(
                Q(codigo__icontains=q) |
                Q(titulo__icontains=q) |
                Q(descripcion__icontains=q)
            )
        if estado:
            queryset = queryset.filter(estado=estado)
        if gravedad:
            queryset = queryset.filter(gravedad=gravedad)
        if fuente:
            queryset = queryset.filter(fuente=fuente)
        if vencidas == '1':
            from django.utils import timezone
            queryset = queryset.filter(
                estado__in=['abierta', 'en_investigacion', 'en_tratamiento'],
                fecha_limite_resolucion__lt=timezone.localdate(),
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters'] = self.request.GET
        context['estado_choices'] = NoConformidad.Estado.choices
        context['gravedad_choices'] = NoConformidad.Gravedad.choices
        context['fuente_choices'] = NoConformidad.Fuente.choices
        return context


class NCDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = NoConformidad
    template_name = 'corrective_actions/nc_detail.html'
    context_object_name = 'nc'
    login_url = '/login/'
    company_field_name = 'empresa'


class NCCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = NoConformidad
    form_class = NoConformidadForm
    template_name = 'corrective_actions/nc_form.html'
    success_url = reverse_lazy('corrective_actions:nc-list')
    login_url = '/login/'
    company_field_name = 'empresa'

    def form_valid(self, form):
        empresa = self.get_active_company()
        if empresa:
            form.instance.empresa = empresa
            form.instance.codigo = generar_codigo_nc(empresa)
        form.instance.creado_por = self.request.user
        return super().form_valid(form)


class NCUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = NoConformidad
    form_class = NoConformidadForm
    template_name = 'corrective_actions/nc_form.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_success_url(self):
        return reverse_lazy('corrective_actions:nc-detail', kwargs={'pk': self.object.pk})


class NCDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = NoConformidad
    template_name = 'corrective_actions/nc_confirm_delete.html'
    success_url = reverse_lazy('corrective_actions:nc-list')
    login_url = '/login/'
    company_field_name = 'empresa'


class NCCerrarView(LoginRequiredMixin, CompanyScopedMixin, FormView):
    form_class = NoConformidadCerrarForm
    template_name = 'corrective_actions/nc_cerrar.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_nc(self):
        return NoConformidad.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nc'] = self.get_nc()
        return context

    def form_valid(self, form):
        nc = self.get_nc()
        nc.estado = NoConformidad.Estado.CERRADA
        nc.resuelta_en = form.cleaned_data['resuelta_en']
        nc.verificada = True
        nc.fecha_verificacion = form.cleaned_data['resuelta_en']
        nc.verificada_por = self.request.user
        nc.notas_verificacion = form.cleaned_data.get('notas_verificacion', '')
        nc.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('corrective_actions:nc-detail', kwargs={'pk': self.kwargs['pk']})


# =========================================================
# ACCIONES CORRECTIVAS
# =========================================================


class ACListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = AccionCorrectiva
    template_name = 'corrective_actions/ac_list.html'
    context_object_name = 'acciones'
    paginate_by = 20
    login_url = '/login/'
    company_field_name = 'no_conformidad__empresa'

    def get_queryset(self):
        queryset = AccionCorrectiva.objects.select_related(
            'no_conformidad', 'no_conformidad__empresa', 'responsable',
        )
        queryset = self.get_company_scoped_queryset(queryset)

        estado = self.request.GET.get('estado', '').strip()
        vencidas = self.request.GET.get('vencidas', '').strip()

        if estado:
            queryset = queryset.filter(estado=estado)
        if vencidas == '1':
            from django.utils import timezone
            queryset = queryset.filter(
                estado__in=['pendiente', 'en_progreso'],
                fecha_limite__lt=timezone.localdate(),
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters'] = self.request.GET
        context['estado_choices'] = AccionCorrectiva.Estado.choices
        return context


class ACDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = AccionCorrectiva
    template_name = 'corrective_actions/ac_detail.html'
    context_object_name = 'accion'
    login_url = '/login/'
    company_field_name = 'no_conformidad__empresa'


class ACCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = AccionCorrectiva
    form_class = AccionCorrectivaForm
    template_name = 'corrective_actions/ac_form.html'
    login_url = '/login/'
    company_field_name = 'no_conformidad__empresa'

    def get_nc(self):
        return NoConformidad.objects.get(pk=self.kwargs['nc_pk'])

    def form_valid(self, form):
        form.instance.no_conformidad = self.get_nc()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('corrective_actions:nc-detail', kwargs={'pk': self.kwargs['nc_pk']})


class ACUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = AccionCorrectiva
    form_class = AccionCorrectivaForm
    template_name = 'corrective_actions/ac_form.html'
    login_url = '/login/'
    company_field_name = 'no_conformidad__empresa'

    def get_success_url(self):
        return reverse_lazy('corrective_actions:ac-detail', kwargs={'pk': self.object.pk})


class ACDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = AccionCorrectiva
    template_name = 'corrective_actions/ac_confirm_delete.html'
    login_url = '/login/'
    company_field_name = 'no_conformidad__empresa'

    def get_success_url(self):
        return reverse_lazy('corrective_actions:nc-detail', kwargs={'pk': self.object.no_conformidad.pk})


# =========================================================
# ACCIONES PREVENTIVAS
# =========================================================


class APListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = AccionPreventiva
    template_name = 'corrective_actions/ap_list.html'
    context_object_name = 'acciones'
    paginate_by = 20
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_queryset(self):
        queryset = AccionPreventiva.objects.select_related(
            'empresa', 'responsable', 'no_conformidad_origen',
        )
        queryset = self.get_company_scoped_queryset(queryset)

        estado = self.request.GET.get('estado', '').strip()
        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters'] = self.request.GET
        context['estado_choices'] = AccionPreventiva.Estado.choices
        return context


class APDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = AccionPreventiva
    template_name = 'corrective_actions/ap_detail.html'
    context_object_name = 'accion'
    login_url = '/login/'
    company_field_name = 'empresa'


class APCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = AccionPreventiva
    form_class = AccionPreventivaForm
    template_name = 'corrective_actions/ap_form.html'
    success_url = reverse_lazy('corrective_actions:ap-list')
    login_url = '/login/'
    company_field_name = 'empresa'

    def form_valid(self, form):
        empresa = self.get_active_company()
        if empresa:
            form.instance.empresa = empresa
        return super().form_valid(form)


class APUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = AccionPreventiva
    form_class = AccionPreventivaForm
    template_name = 'corrective_actions/ap_form.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_success_url(self):
        return reverse_lazy('corrective_actions:ap-detail', kwargs={'pk': self.object.pk})


class APDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = AccionPreventiva
    template_name = 'corrective_actions/ap_confirm_delete.html'
    success_url = reverse_lazy('corrective_actions:ap-list')
    login_url = '/login/'
    company_field_name = 'empresa'
