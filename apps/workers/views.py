from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import Q

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
    login_url = '/admin/login/'
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
    login_url = '/admin/login/'
    company_field_name = 'company'

    def get_queryset(self):
        queryset = Worker.objects.select_related(
            'company',
            'work_center',
            'job_position',
        )
        return self.get_company_scoped_queryset(queryset)


class WorkerCreateView(LoginRequiredMixin, CreateView):
    model = Worker
    form_class = WorkerForm
    template_name = 'workers/worker_form.html'
    success_url = reverse_lazy('worker-list')


class WorkerUpdateView(LoginRequiredMixin, UpdateView):
    model = Worker
    form_class = WorkerForm
    template_name = 'workers/worker_form.html'

    def get_success_url(self):
        return reverse_lazy('worker-detail', kwargs={'pk': self.object.pk})


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


class JobPositionListView(LoginRequiredMixin, ListView):
    model = JobPosition
    template_name = 'workers/jobposition_list.html'
    context_object_name = 'positions'
    ordering = ['company__trade_name', 'name']

    def get_queryset(self):
        return JobPosition.objects.select_related('company').order_by('company__trade_name', 'name')


class JobPositionDetailView(LoginRequiredMixin, DetailView):
    model = JobPosition
    template_name = 'workers/jobposition_detail.html'
    context_object_name = 'position'

    def get_queryset(self):
        return JobPosition.objects.select_related('company')


class JobPositionCreateView(LoginRequiredMixin, CreateView):
    model = JobPosition
    form_class = JobPositionForm
    template_name = 'workers/jobposition_form.html'
    success_url = reverse_lazy('jobposition-list')


class JobPositionUpdateView(LoginRequiredMixin, UpdateView):
    model = JobPosition
    form_class = JobPositionForm
    template_name = 'workers/jobposition_form.html'

    def get_success_url(self):
        return reverse_lazy('jobposition-detail', kwargs={'pk': self.object.pk})