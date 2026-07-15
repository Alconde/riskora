from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.http import HttpResponse
from django.db.models import Q

from apps.core.mixins import CompanyScopedMixin
from .models import Accidente, InvestigacionAccidente, CausaAccidente, Incidente, ProcedimientoInvestigacion
from .forms import (
    AccidenteForm, InvestigacionAccidenteForm,
    CausaAccidenteForm, IncidenteForm, ProcedimientoInvestigacionForm,
)
from .services import (
    generar_codigo_accidente, generar_codigo_incidente,
    generar_nc_desde_accidente, calcular_estadisticas_accidentes,
)


# =========================================================
# DASHBOARD
# =========================================================


class IncidentsDashboardView(LoginRequiredMixin, CompanyScopedMixin, TemplateView):
    template_name = 'incidents/dashboard.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = self.get_active_company()
        stats = calcular_estadisticas_accidentes(empresa)
        context['stats'] = stats

        if empresa:
            context['procedimiento'] = ProcedimientoInvestigacion.objects.filter(
                empresa=empresa, activo=True
            ).order_by('-created_at').first()
            context['total_causas'] = CausaAccidente.objects.filter(
                Q(empresa=empresa) | Q(empresa__isnull=True), activa=True
            ).count()
            context['ultimos_accidentes'] = Accidente.objects.filter(
                empresa=empresa
            ).select_related('centro_trabajo')[:5]
            context['ultimos_incidentes'] = Incidente.objects.filter(
                empresa=empresa
            ).select_related('centro_trabajo')[:5]
        else:
            context['procedimiento'] = None
            context['total_causas'] = CausaAccidente.objects.filter(
                empresa__isnull=True, activa=True
            ).count()
            context['ultimos_accidentes'] = []
            context['ultimos_incidentes'] = []

        return context


class ProcedimientoInvestigacionCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = ProcedimientoInvestigacion
    form_class = ProcedimientoInvestigacionForm
    template_name = 'incidents/procedimiento_form.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def form_valid(self, form):
        empresa = self.get_active_company()
        if empresa:
            form.instance.empresa = empresa
        form.instance.subido_por = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('incidents:dashboard')


class ProcedimientoInvestigacionUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = ProcedimientoInvestigacion
    form_class = ProcedimientoInvestigacionForm
    template_name = 'incidents/procedimiento_form.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_success_url(self):
        return reverse_lazy('incidents:dashboard')


def imprimir_investigacion_blanco(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="formulario_investigacion_blanco.pdf"'
    from .services import generar_pdf_investigacion_blanco
    generar_pdf_investigacion_blanco(response)
    return response


def descargar_investigacion_pdf(request, pk):
    investigacion = InvestigacionAccidente.objects.select_related(
        'accidente', 'accidente__empresa', 'accidente__centro_trabajo',
        'accidente__trabajador_afectado', 'investigador', 'revisor', 'responsable',
    ).get(pk=pk)
    response = HttpResponse(content_type='application/pdf')
    filename = f'investigacion_{investigacion.accidente.codigo}.pdf'
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    from .services import generar_pdf_investigacion
    generar_pdf_investigacion(investigacion, response)
    return response


# =========================================================
# ACCIDENTES
# =========================================================


class AccidenteListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = Accidente
    template_name = 'incidents/accidente_list.html'
    context_object_name = 'accidentes'
    paginate_by = 20
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_queryset(self):
        queryset = Accidente.objects.select_related(
            'empresa', 'centro_trabajo', 'trabajador_afectado', 'creado_por',
        )
        queryset = self.get_company_scoped_queryset(queryset)

        q = self.request.GET.get('q', '').strip()
        estado = self.request.GET.get('estado', '').strip()
        gravedad = self.request.GET.get('gravedad', '').strip()
        tipo = self.request.GET.get('tipo', '').strip()
        centro = self.request.GET.get('centro', '').strip()

        if q:
            queryset = queryset.filter(
                Q(titulo__icontains=q) |
                Q(descripcion__icontains=q) |
                Q(codigo__icontains=q)
            )
        if estado:
            queryset = queryset.filter(estado=estado)
        if gravedad:
            queryset = queryset.filter(gravedad=gravedad)
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        if centro:
            queryset = queryset.filter(centro_trabajo_id=centro)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters'] = self.request.GET
        context['estado_choices'] = Accidente.Estado.choices
        context['gravedad_choices'] = Accidente.Gravedad.choices
        context['tipo_choices'] = Accidente.Tipo.choices
        empresa = self.get_active_company()
        if empresa:
            from apps.workcenters.models import WorkCenter
            context['centros'] = WorkCenter.objects.filter(company=empresa)
        return context


class AccidenteDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = Accidente
    template_name = 'incidents/accidente_detail.html'
    context_object_name = 'accidente'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['investigacion_form'] = InvestigacionAccidenteForm()
        return context


class AccidenteCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = Accidente
    form_class = AccidenteForm
    template_name = 'incidents/accidente_form.html'
    success_url = reverse_lazy('incidents:accidente-list')
    login_url = '/login/'
    company_field_name = 'empresa'

    def form_valid(self, form):
        empresa = self.get_active_company()
        if empresa:
            form.instance.empresa = empresa
            form.instance.codigo = generar_codigo_accidente(empresa)
        form.instance.creado_por = self.request.user
        return super().form_valid(form)


class AccidenteUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = Accidente
    form_class = AccidenteForm
    template_name = 'incidents/accidente_form.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_success_url(self):
        return reverse_lazy('incidents:accidente-detail', kwargs={'pk': self.object.pk})


class AccidenteDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = Accidente
    template_name = 'incidents/accidente_confirm_delete.html'
    success_url = reverse_lazy('incidents:accidente-list')
    login_url = '/login/'
    company_field_name = 'empresa'


class AccidenteNCView(LoginRequiredMixin, CreateView):
    from apps.corrective_actions.models import NoConformidad
    from apps.corrective_actions.forms import NoConformidadForm
    model = NoConformidad
    form_class = NoConformidadForm
    template_name = 'incidents/accidente_nc.html'
    login_url = '/login/'

    def get_accidente(self):
        return Accidente.objects.get(pk=self.kwargs['accidente_pk'])

    def form_valid(self, form):
        accidente = self.get_accidente()
        nc = generar_nc_desde_accidente(
            accidente, self.request.user,
            form_data={
                'titulo': form.cleaned_data.get('titulo'),
                'descripcion': form.cleaned_data.get('descripcion'),
                'gravedad': form.cleaned_data.get('gravedad'),
                'fecha_limite_resolucion': form.cleaned_data.get('fecha_limite_resolucion'),
            },
        )
        from django.shortcuts import redirect
        return redirect('corrective_actions:nc-detail', pk=nc.pk)


# =========================================================
# INVESTIGACION DE ACCIDENTES
# =========================================================


class InvestigacionCreateView(LoginRequiredMixin, CreateView):
    model = InvestigacionAccidente
    form_class = InvestigacionAccidenteForm
    template_name = 'incidents/investigacion_form.html'
    login_url = '/login/'

    def form_valid(self, form):
        accidente = Accidente.objects.get(pk=self.kwargs['accidente_pk'])
        form.instance.accidente = accidente
        form.instance.investigador = self.request.user
        accidente.estado = Accidente.Estado.EN_INVESTIGACION
        accidente.save(update_fields=['estado', 'updated_at'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'incidents:accidente-detail',
            kwargs={'pk': self.kwargs['accidente_pk']},
        )


class InvestigacionUpdateView(LoginRequiredMixin, UpdateView):
    model = InvestigacionAccidente
    form_class = InvestigacionAccidenteForm
    template_name = 'incidents/investigacion_form.html'
    login_url = '/login/'

    def get_success_url(self):
        return reverse_lazy(
            'incidents:accidente-detail',
            kwargs={'pk': self.object.accidente.pk},
        )


class InvestigacionDetailView(LoginRequiredMixin, DetailView):
    model = InvestigacionAccidente
    template_name = 'incidents/investigacion_detail.html'
    context_object_name = 'investigacion'
    login_url = '/login/'


# =========================================================
# CAUSAS DE ACCIDENTES
# =========================================================


class CausaListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = CausaAccidente
    template_name = 'incidents/causa_list.html'
    context_object_name = 'causas'
    paginate_by = 20
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_queryset(self):
        empresa = self.get_active_company()
        queryset = CausaAccidente.objects.filter(
            Q(empresa=empresa) | Q(empresa__isnull=True)
        ) if empresa else CausaAccidente.objects.filter(empresa__isnull=True)

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
        context['categoria_choices'] = CausaAccidente.Categoria.choices
        return context


class CausaCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = CausaAccidente
    form_class = CausaAccidenteForm
    template_name = 'incidents/causa_form.html'
    success_url = reverse_lazy('incidents:causa-list')
    login_url = '/login/'
    company_field_name = 'empresa'

    def form_valid(self, form):
        empresa = self.get_active_company()
        if empresa:
            form.instance.empresa = empresa
        return super().form_valid(form)


class CausaUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = CausaAccidente
    form_class = CausaAccidenteForm
    template_name = 'incidents/causa_form.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_success_url(self):
        return reverse_lazy('incidents:causa-list')


class CausaDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = CausaAccidente
    template_name = 'incidents/causa_confirm_delete.html'
    success_url = reverse_lazy('incidents:causa-list')
    login_url = '/login/'
    company_field_name = 'empresa'


# =========================================================
# INCIDENTES
# =========================================================


class IncidenteListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = Incidente
    template_name = 'incidents/incidente_list.html'
    context_object_name = 'incidentes'
    paginate_by = 20
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_queryset(self):
        queryset = Incidente.objects.select_related(
            'empresa', 'centro_trabajo', 'trabajador_reports', 'creado_por',
        )
        queryset = self.get_company_scoped_queryset(queryset)

        q = self.request.GET.get('q', '').strip()
        estado = self.request.GET.get('estado', '').strip()
        gravedad = self.request.GET.get('gravedad', '').strip()
        centro = self.request.GET.get('centro', '').strip()

        if q:
            queryset = queryset.filter(
                Q(titulo__icontains=q) |
                Q(descripcion__icontains=q) |
                Q(codigo__icontains=q)
            )
        if estado:
            queryset = queryset.filter(estado=estado)
        if gravedad:
            queryset = queryset.filter(gravedad_potencial=gravedad)
        if centro:
            queryset = queryset.filter(centro_trabajo_id=centro)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters'] = self.request.GET
        context['estado_choices'] = Incidente.Estado.choices
        context['gravedad_choices'] = Incidente.GravedadPotencial.choices
        empresa = self.get_active_company()
        if empresa:
            from apps.workcenters.models import WorkCenter
            context['centros'] = WorkCenter.objects.filter(company=empresa)
        return context


class IncidenteDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = Incidente
    template_name = 'incidents/incidente_detail.html'
    context_object_name = 'incidente'
    login_url = '/login/'
    company_field_name = 'empresa'


class IncidenteCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = Incidente
    form_class = IncidenteForm
    template_name = 'incidents/incidente_form.html'
    success_url = reverse_lazy('incidents:incidente-list')
    login_url = '/login/'
    company_field_name = 'empresa'

    def form_valid(self, form):
        empresa = self.get_active_company()
        if empresa:
            form.instance.empresa = empresa
            form.instance.codigo = generar_codigo_incidente(empresa)
        form.instance.creado_por = self.request.user
        return super().form_valid(form)


class IncidenteUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = Incidente
    form_class = IncidenteForm
    template_name = 'incidents/incidente_form.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_success_url(self):
        return reverse_lazy('incidents:incidente-detail', kwargs={'pk': self.object.pk})


class IncidenteDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = Incidente
    template_name = 'incidents/incidente_confirm_delete.html'
    success_url = reverse_lazy('incidents:incidente-list')
    login_url = '/login/'
    company_field_name = 'empresa'


@login_required(login_url='/login/')
def exportar_accidentes_excel(request):
    from apps.core.export import exportar_excel

    empresa = getattr(request, 'active_company', None)
    qs = Accidente.objects.select_related('empresa', 'centro_trabajo', 'trabajador_afectado', 'creado_por')
    if empresa:
        qs = qs.filter(empresa=empresa)
    else:
        qs = qs.none()

    columns = [
        {'header': 'Codigo', 'value': lambda a: a.codigo, 'width': 15},
        {'header': 'Titulo', 'value': lambda a: a.titulo, 'width': 35},
        {'header': 'Empresa', 'value': lambda a: str(a.empresa), 'width': 25},
        {'header': 'Centro', 'value': lambda a: str(a.centro_trabajo) if a.centro_trabajo else '', 'width': 25},
        {'header': 'Fecha', 'value': lambda a: a.fecha.strftime('%d/%m/%Y %H:%M') if a.fecha else '', 'width': 18},
        {'header': 'Tipo', 'value': lambda a: a.get_tipo_display(), 'width': 18},
        {'header': 'Gravedad', 'value': lambda a: a.get_gravedad_display(), 'width': 15},
        {'header': 'Tipo Lesion', 'value': lambda a: a.get_tipo_lesion_display(), 'width': 15},
        {'header': 'Ubicacion', 'value': lambda a: a.ubicacion or '', 'width': 20},
        {'header': 'Trabajador', 'value': lambda a: str(a.trabajador_afectado) if a.trabajador_afectado else '', 'width': 20},
        {'header': 'Estado', 'value': lambda a: a.get_estado_display(), 'width': 15},
    ]

    subtitle = f'Empresa: {empresa}' if empresa else 'Sin empresa activa'
    return exportar_excel(
        queryset=qs,
        columns=columns,
        title='Accidentes de Trabajo',
        filename='accidentes.xlsx',
        subtitle=subtitle,
    )
