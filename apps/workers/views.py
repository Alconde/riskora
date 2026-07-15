from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.db.models import Q, Prefetch

from apps.workers.forms import WorkerForm
from apps.workers.models import Worker, JobPosition
from apps.workcenters.models import WorkCenter
from apps.workers.forms_job_position import JobPositionForm
from apps.companies.models import Company
from apps.core.mixins import CompanyScopedMixin


class WorkerListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = Worker
    template_name = 'workers/worker_list.html'
    context_object_name = 'workers'
    paginate_by = 20
    login_url = '/login/'
    company_field_name = 'company'

    def get_base_queryset(self):
        return Worker.objects.select_related(
            'company',
            'work_center',
            'job_position',
        ).order_by('last_name', 'first_name')

    def get_queryset(self):
        queryset = self.get_company_scoped_queryset(self.get_base_queryset())

        q = self.request.GET.get('q', '').strip()
        company = self.request.GET.get('company', '').strip()
        status = self.request.GET.get('status', '').strip()
        work_center = self.request.GET.get('work_center', '').strip()
        job_position = self.request.GET.get('job_position', '').strip()

        if q:
            queryset = queryset.filter(
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(national_id__icontains=q) |
                Q(email__icontains=q) |
                Q(employee_code__icontains=q)
            )

        if company and self.request.user.is_superuser:
            queryset = queryset.filter(company_id=company)

        if status:
            queryset = queryset.filter(employment_status=status)

        if work_center:
            queryset = queryset.filter(work_center_id=work_center)

        if job_position:
            queryset = queryset.filter(job_position_id=job_position)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters'] = self.request.GET
        context['status_choices'] = Worker.EmploymentStatus.choices

        active_company = self.get_active_company()

        if self.request.user.is_superuser:
            context['companies'] = Company.objects.order_by('legal_name')
            if active_company:
                context['work_centers'] = WorkCenter.objects.filter(company=active_company).order_by('name')
                context['job_positions'] = JobPosition.objects.filter(company=active_company).order_by('name')
            else:
                context['work_centers'] = WorkCenter.objects.order_by('name')
                context['job_positions'] = JobPosition.objects.order_by('name')
        else:
            context['companies'] = Company.objects.filter(
                id=getattr(active_company, 'id', None)
            )

            if active_company:
                context['work_centers'] = WorkCenter.objects.filter(company=active_company).order_by('name')
                context['job_positions'] = JobPosition.objects.filter(company=active_company).order_by('name')
            else:
                context['work_centers'] = WorkCenter.objects.none()
                context['job_positions'] = JobPosition.objects.none()

        return context


class WorkerDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = Worker
    template_name = 'workers/worker_detail.html'
    context_object_name = 'worker'
    login_url = '/login/'
    company_field_name = 'company'

    def get_queryset(self):
        queryset = Worker.objects.select_related(
            'company',
            'work_center',
            'job_position',
        )
        return self.get_company_scoped_queryset(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.utils import timezone
        from django.db.models import Q
        from apps.authorizations.models import AutorizacionTrabajador
        hoy = timezone.now().date()
        empresa = getattr(self.object, 'company', None)
        autorizaciones = AutorizacionTrabajador.objects.filter(
            trabajador=self.object,
            empresa=empresa,
        ).select_related('requisito').order_by('requisito__nombre')
        context['autorizaciones_recientes'] = autorizaciones[:6]
        context['total_autorizaciones'] = autorizaciones.filter(activa=True).count()
        context['autorizaciones_validas'] = autorizaciones.filter(
            activa=True,
        ).filter(
            Q(fecha_caducidad__isnull=True) | Q(fecha_caducidad__gte=hoy),
        ).count()
        return context


class WorkerCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = Worker
    form_class = WorkerForm
    template_name = 'workers/worker_form.html'
    success_url = reverse_lazy('workers:worker-list')
    login_url = '/login/'
    company_field_name = 'company'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        active_company = self.get_active_company()
        if active_company:
            if self.request.method == 'GET':
                kwargs['initial'] = {'company': active_company}
        return kwargs

    def form_valid(self, form):
        active_company = self.get_active_company()
        if active_company:
            form.instance.company = active_company
        return super().form_valid(form)


class WorkerUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = Worker
    form_class = WorkerForm
    template_name = 'workers/worker_form.html'
    login_url = '/login/'
    company_field_name = 'company'

    def get_queryset(self):
        return self.get_company_scoped_queryset(
            Worker.objects.select_related('company', 'work_center', 'job_position')
        )

    def get_success_url(self):
        return reverse_lazy('workers:worker-detail', kwargs={'pk': self.object.pk})


def load_workcenters(request):
    company_id = request.GET.get('company_id')
    results = []

    if company_id:
        centers = WorkCenter.objects.filter(company_id=company_id).order_by('name')
        results = [{'id': center.id, 'name': center.name} for center in centers]

    return JsonResponse({'results': results})


def load_jobpositions(request):
    company_id = request.GET.get('company_id')
    results = []

    if company_id:
        positions = JobPosition.objects.filter(company_id=company_id).order_by('name')
        results = [{'id': position.id, 'name': position.name} for position in positions]

    return JsonResponse({'results': results})


class JobPositionListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = JobPosition
    template_name = 'workers/jobposition_list.html'
    context_object_name = 'positions'
    login_url = '/login/'
    company_field_name = 'company'

    def get_base_queryset(self):
        return JobPosition.objects.select_related('company')

    def get_queryset(self):
        return self.get_company_scoped_queryset(
            self.get_base_queryset().order_by('company__trade_name', 'name')
        )


class JobPositionDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = JobPosition
    template_name = 'workers/jobposition_detail.html'
    context_object_name = 'position'
    login_url = '/login/'
    company_field_name = 'company'

    def get_queryset(self):
        return self.get_company_scoped_queryset(
            JobPosition.objects.select_related('company')
        )


class JobPositionCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = JobPosition
    form_class = JobPositionForm
    template_name = 'workers/jobposition_form.html'
    success_url = reverse_lazy('workers:jobposition-list')
    login_url = '/login/'
    company_field_name = 'company'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        active_company = self.get_active_company()
        if active_company and self.request.method == 'GET':
            kwargs['initial'] = {'company': active_company}
        return kwargs

    def form_valid(self, form):
        active_company = self.get_active_company()
        if active_company:
            form.instance.company = active_company
        return super().form_valid(form)


class JobPositionUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = JobPosition
    form_class = JobPositionForm
    template_name = 'workers/jobposition_form.html'
    login_url = '/login/'
    company_field_name = 'company'

    def get_queryset(self):
        return self.get_company_scoped_queryset(
            JobPosition.objects.select_related('company')
        )

    def get_success_url(self):
        return reverse_lazy('workers:jobposition-detail', kwargs={'pk': self.object.pk})


class WorkerDocumentsView(LoginRequiredMixin, CompanyScopedMixin, TemplateView):
    template_name = 'workers/worker_documents.html'
    login_url = '/login/'
    company_field_name = 'company'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        workers_qs = self.get_company_scoped_queryset(
            Worker.objects.select_related(
                'company', 'work_center', 'job_position'
            ).order_by('last_name', 'first_name')
        )
        context['workers'] = workers_qs

        worker_id = self.request.GET.get('worker')
        selected_worker = None
        documents = {'training': [], 'health': [], 'epi_deliveries': [], 'risk_items': []}

        if worker_id:
            try:
                selected_worker = workers_qs.get(pk=worker_id)
            except Worker.DoesNotExist:
                pass

        if selected_worker:
            training_records = selected_worker.training_records.select_related(
                'course', 'evidence_document'
            ).prefetch_related('documents').order_by('-completed_date', '-planned_date')

            health_records = selected_worker.reconocimientos_medicos.select_related(
                'company'
            ).order_by('-fecha')

            epi_deliveries = selected_worker.entregas_epi.select_related(
                'epi', 'epi__catalogo', 'firma'
            ).order_by('-fecha_entrega')

            risk_items = []
            if selected_worker.job_position:
                risk_items = list(
                    selected_worker.job_position.items_evaluacion.select_related(
                        'evaluacion', 'tipo_peligro'
                    ).filter(
                        evaluacion__estado='aprobada'
                    ).order_by('-nivel_riesgo', 'factor_riesgo_condicion')[:50]
                )

            documents = {
                'training': training_records,
                'health': health_records,
                'epi_deliveries': epi_deliveries,
                'risk_items': risk_items,
            }

        context['selected_worker'] = selected_worker
        context['documents'] = documents
        context['filters'] = self.request.GET
        return context


class WorkerDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = Worker
    template_name = 'workers/worker_confirm_delete.html'
    success_url = reverse_lazy('workers:worker-list')
    login_url = '/login/'
    company_field_name = 'company'

    def get_queryset(self):
        return self.get_company_scoped_queryset(
            Worker.objects.select_related('company')
        )

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Trabajador eliminado correctamente.')
        return super().delete(request, *args, **kwargs)


class JobPositionDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = JobPosition
    template_name = 'workers/jobposition_confirm_delete.html'
    success_url = reverse_lazy('workers:jobposition-list')
    login_url = '/login/'
    company_field_name = 'company'

    def get_queryset(self):
        return self.get_company_scoped_queryset(
            JobPosition.objects.select_related('company')
        )

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Puesto de trabajo eliminado correctamente.')
        return super().delete(request, *args, **kwargs)