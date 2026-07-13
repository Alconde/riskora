from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.http import HttpResponse
from django.db.models import Q

from apps.core.mixins import CompanyScopedMixin
from .models import EnfermedadProfesional, InvestigacionEEPP, ProcedimientoInvestigacionEEPP
from .forms import EnfermedadProfesionalForm, InvestigacionEEPPForm, ProcedimientoInvestigacionEEPPForm
from .services import generar_codigo_eepp, calcular_estadisticas_eepp


class EppsDashboardView(LoginRequiredMixin, CompanyScopedMixin, TemplateView):
    template_name = 'epps/dashboard.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = self.get_active_company()
        stats = calcular_estadisticas_eepp(empresa)
        context['stats'] = stats

        if empresa:
            context['procedimiento'] = ProcedimientoInvestigacionEEPP.objects.filter(
                empresa=empresa, activo=True
            ).order_by('-created_at').first()
            context['ultimas_eepp'] = EnfermedadProfesional.objects.filter(
                empresa=empresa
            ).select_related('centro_trabajo')[:5]
        else:
            context['procedimiento'] = None
            context['ultimas_eepp'] = []

        return context


class EnfermedadProfesionalListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = EnfermedadProfesional
    template_name = 'epps/enfermedad_list.html'
    context_object_name = 'enfermedades'
    login_url = '/login/'
    company_field_name = 'empresa'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related('centro_trabajo', 'trabajador_afectado')
        empresa = self.get_active_company()
        if empresa:
            qs = qs.filter(empresa=empresa)

        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(codigo__icontains=q) |
                Q(titulo__icontains=q) |
                Q(nombre_enfermedad__icontains=q)
            )

        estado = self.request.GET.get('estado', '')
        if estado:
            qs = qs.filter(estado=estado)

        agente = self.request.GET.get('agente', '')
        if agente:
            qs = qs.filter(agente_causante=agente)

        return qs


class EnfermedadProfesionalDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = EnfermedadProfesional
    template_name = 'epps/enfermedad_detail.html'
    context_object_name = 'enfermedad'
    login_url = '/login/'
    company_field_name = 'empresa'


class EnfermedadProfesionalCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = EnfermedadProfesional
    form_class = EnfermedadProfesionalForm
    template_name = 'epps/enfermedad_form.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def form_valid(self, form):
        empresa = self.get_active_company()
        if empresa:
            form.instance.empresa = empresa
            form.instance.codigo = generar_codigo_eepp(empresa)
        form.instance.creado_por = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.get_active_company()
        return kwargs

    def get_success_url(self):
        return reverse_lazy('epps:enfermedad-detail', kwargs={'pk': self.object.pk})


class EnfermedadProfesionalUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = EnfermedadProfesional
    form_class = EnfermedadProfesionalForm
    template_name = 'epps/enfermedad_form.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.get_active_company()
        return kwargs

    def get_success_url(self):
        return reverse_lazy('epps:enfermedad-detail', kwargs={'pk': self.object.pk})


class EnfermedadProfesionalDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = EnfermedadProfesional
    template_name = 'epps/enfermedad_confirm_delete.html'
    login_url = '/login/'
    company_field_name = 'empresa'
    success_url = reverse_lazy('epps:enfermedad-list')


class InvestigacionEEPPCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = InvestigacionEEPP
    form_class = InvestigacionEEPPForm
    template_name = 'epps/investigacion_form.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_queryset(self):
        return super().get_queryset().select_related('enfermedad')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enfermedad'] = EnfermedadProfesional.objects.get(pk=self.kwargs['eepp_pk'])
        return context

    def form_valid(self, form):
        empresa = self.get_active_company()
        enfermedad = EnfermedadProfesional.objects.get(pk=self.kwargs['eepp_pk'])
        form.instance.enfermedad = enfermedad
        if empresa:
            pass
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.get_active_company()
        return kwargs

    def get_success_url(self):
        return reverse_lazy('epps:investigacion-detail', kwargs={'pk': self.object.pk})


class InvestigacionEEPPUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = InvestigacionEEPP
    form_class = InvestigacionEEPPForm
    template_name = 'epps/investigacion_form.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_queryset(self):
        return super().get_queryset().select_related('enfermedad')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.get_active_company()
        return kwargs

    def get_success_url(self):
        return reverse_lazy('epps:investigacion-detail', kwargs={'pk': self.object.pk})


class InvestigacionEEPPDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = InvestigacionEEPP
    template_name = 'epps/investigacion_detail.html'
    context_object_name = 'investigacion'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_queryset(self):
        return super().get_queryset().select_related(
            'enfermedad', 'enfermedad__empresa', 'enfermedad__centro_trabajo',
            'enfermedad__trabajador_afectado', 'investigador', 'revisor', 'responsable',
        )


class ProcedimientoEEPPCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = ProcedimientoInvestigacionEEPP
    form_class = ProcedimientoInvestigacionEEPPForm
    template_name = 'epps/procedimiento_form.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def form_valid(self, form):
        empresa = self.get_active_company()
        if empresa:
            form.instance.empresa = empresa
        form.instance.subido_por = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('epps:dashboard')


class ProcedimientoEEPPUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = ProcedimientoInvestigacionEEPP
    form_class = ProcedimientoInvestigacionEEPPForm
    template_name = 'epps/procedimiento_form.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_success_url(self):
        return reverse_lazy('epps:dashboard')


def imprimir_eepp_blanco(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="formulario_investigacion_eepp_blanco.pdf"'
    from .services import generar_pdf_eepp_blanco
    generar_pdf_eepp_blanco(response)
    return response


def descargar_eepp_pdf(request, pk):
    investigacion = InvestigacionEEPP.objects.select_related(
        'enfermedad', 'enfermedad__empresa', 'enfermedad__centro_trabajo',
        'enfermedad__trabajador_afectado', 'investigador', 'revisor', 'responsable',
    ).get(pk=pk)
    response = HttpResponse(content_type='application/pdf')
    filename = f'investigacion_eepp_{investigacion.enfermedad.codigo}.pdf'
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    from .services import generar_pdf_eepp
    generar_pdf_eepp(investigacion, response)
    return response
