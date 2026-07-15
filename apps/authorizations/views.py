from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q, Count

from apps.core.mixins import CompanyScopedMixin
from .models import RequisitoAutorizacion, AutorizacionTrabajador
from .forms import RequisitoAutorizacionForm, AutorizacionTrabajadorForm


class AutorizacionDashboardView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = RequisitoAutorizacion
    template_name = 'authorizations/dashboard.html'
    context_object_name = 'requisitos'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_queryset(self):
        qs = super().get_queryset()
        empresa = self.get_active_company()
        qs = qs.filter(
            Q(empresa__isnull=True) | Q(empresa=empresa),
            activo=True,
        )
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(nombre__icontains=q) | Q(normativa__icontains=q)
            )
        tipo = self.request.GET.get('tipo', '')
        if tipo:
            qs = qs.filter(tipo=tipo)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = self.get_active_company()
        from datetime import timedelta
        from django.utils import timezone
        from apps.workers.models import Worker

        hoy = timezone.now().date()
        limite_30 = hoy + timedelta(days=30)

        total_autorizaciones = AutorizacionTrabajador.objects.filter(
            empresa=empresa, activa=True,
        ).count() if empresa else 0
        total_caducadas = AutorizacionTrabajador.objects.filter(
            empresa=empresa, activa=True, fecha_caducidad__lt=hoy,
        ).count() if empresa else 0
        total_proximas = AutorizacionTrabajador.objects.filter(
            empresa=empresa, activa=True,
            fecha_caducidad__gte=hoy, fecha_caducidad__lte=limite_30,
        ).count() if empresa else 0
        total_trabajadores = Worker.objects.filter(
            company=empresa, employment_status='active',
        ).count() if empresa else 0

        context['total_autorizaciones'] = total_autorizaciones
        context['total_caducadas'] = total_caducadas
        context['total_proximas'] = total_proximas
        context['total_trabajadores'] = total_trabajadores
        context['tipos'] = RequisitoAutorizacion.Tipo.choices
        context['tipo_actual'] = self.request.GET.get('tipo', '')
        return context


class RequisitoAutorizacionDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = RequisitoAutorizacion
    template_name = 'authorizations/requisito_detail.html'
    context_object_name = 'requisito'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = self.get_active_company()
        from datetime import timedelta
        from django.utils import timezone
        hoy = timezone.now().date()

        autorizaciones = AutorizacionTrabajador.objects.filter(
            requisito=self.object,
            empresa=empresa,
        ).select_related('trabajador', 'trabajador__job_position')

        filtro = self.request.GET.get('filtro', '')
        if filtro == 'activas':
            autorizaciones = autorizaciones.filter(
                activa=True,
                fecha_autorizacion__lte=hoy,
            ).filter(
                Q(fecha_caducidad__isnull=True) | Q(fecha_caducidad__gte=hoy),
            )
        elif filtro == 'caducadas':
            autorizaciones = autorizaciones.filter(
                activa=True, fecha_caducidad__lt=hoy,
            )
        elif filtro == 'proximas':
            limite = hoy + timedelta(days=30)
            autorizaciones = autorizaciones.filter(
                activa=True,
                fecha_caducidad__gte=hoy,
                fecha_caducidad__lte=limite,
            )

        context['autorizaciones'] = autorizaciones
        context['filtro_actual'] = filtro

        from apps.workers.models import Worker
        autorizados_ids = AutorizacionTrabajador.objects.filter(
            requisito=self.object, empresa=empresa, activa=True,
        ).values_list('trabajador_id', flat=True)
        trabajadores_autorizados = Worker.objects.filter(
            id__in=autorizados_ids, company=empresa, employment_status='active',
        )
        todos_activos = Worker.objects.filter(
            company=empresa, employment_status='active',
        )
        context['total_sin_autorizacion'] = todos_activos.exclude(
            id__in=trabajadores_autorizados
        ).count()
        return context


class RequisitoAutorizacionCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = RequisitoAutorizacion
    form_class = RequisitoAutorizacionForm
    template_name = 'authorizations/requisito_form.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def form_valid(self, form):
        empresa = self.get_active_company()
        form.instance.empresa = empresa
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('authorizations:dashboard')


class RequisitoAutorizacionUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = RequisitoAutorizacion
    form_class = RequisitoAutorizacionForm
    template_name = 'authorizations/requisito_form.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_success_url(self):
        return reverse_lazy('authorizations:requisito-detail', kwargs={'pk': self.object.pk})


class RequisitoAutorizacionDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = RequisitoAutorizacion
    template_name = 'authorizations/requisito_confirm_delete.html'
    login_url = '/login/'
    company_field_name = 'empresa'
    success_url = reverse_lazy('authorizations:dashboard')


class AutorizacionCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = AutorizacionTrabajador
    form_class = AutorizacionTrabajadorForm
    template_name = 'authorizations/autorizacion_form.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_initial(self):
        initial = super().get_initial()
        requisito_pk = self.kwargs.get('requisito_pk')
        if requisito_pk:
            initial['requisito'] = requisito_pk
        return initial

    def form_valid(self, form):
        empresa = self.get_active_company()
        form.instance.empresa = empresa
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.get_active_company()
        return kwargs

    def get_success_url(self):
        requisito = self.object.requisito
        return reverse_lazy('authorizations:requisito-detail', kwargs={'pk': requisito.pk})


class AutorizacionUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = AutorizacionTrabajador
    form_class = AutorizacionTrabajadorForm
    template_name = 'authorizations/autorizacion_form.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.get_active_company()
        return kwargs

    def get_success_url(self):
        return reverse_lazy(
            'authorizations:requisito-detail', kwargs={'pk': self.object.requisito.pk}
        )


class AutorizacionDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = AutorizacionTrabajador
    template_name = 'authorizations/autorizacion_confirm_delete.html'
    login_url = '/login/'
    company_field_name = 'empresa'

    def get_success_url(self):
        return reverse_lazy(
            'authorizations:requisito-detail', kwargs={'pk': self.object.requisito.pk}
        )


class WorkerAutorizacionesView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    """Vista de todas las autorizaciones de un trabajador (accesible desde su perfil)."""
    template_name = 'authorizations/worker_autorizaciones.html'
    context_object_name = 'worker'
    login_url = '/login/'
    company_field_name = 'company'

    def get_queryset(self):
        from apps.workers.models import Worker
        return Worker.objects.select_related('company')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = self.get_active_company()
        autorizaciones = AutorizacionTrabajador.objects.filter(
            trabajador=self.object,
            empresa=empresa,
        ).select_related('requisito').order_by('requisito__nombre')

        from datetime import timedelta
        from django.utils import timezone
        hoy = timezone.now().date()

        context['autorizaciones'] = autorizaciones
        context['autorizaciones_activas'] = autorizaciones.filter(
            activa=True,
        ).filter(
            Q(fecha_caducidad__isnull=True) | Q(fecha_caducidad__gte=hoy),
        ).count()
        context['autorizaciones_caducadas'] = autorizaciones.filter(
            activa=True, fecha_caducidad__lt=hoy,
        ).count()
        context['autorizaciones_proximas'] = autorizaciones.filter(
            activa=True,
            fecha_caducidad__gte=hoy,
            fecha_caducidad__lte=hoy + timedelta(days=30),
        ).count()
        return context
