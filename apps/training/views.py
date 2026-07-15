from datetime import timedelta
from urllib.parse import urlencode

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView, DetailView, ListView, CreateView, UpdateView, DeleteView

from apps.companies.models import Company
from apps.core.mixins import CompanyScopedMixin

from .forms import (
    TrainingCategoryForm,
    TrainingCourseForm,
    TrainingRecordForm,
)
from .models import TrainingCategory, TrainingCourse, TrainingRecord, TrainingNeed, TrainingAlert


# =========================================================
# CATEGORÍAS
# =========================================================




class TrainingCategoryListView(LoginRequiredMixin, ListView):
    model = TrainingCategory
    template_name = 'training/category_list.html'
    context_object_name = 'categories'
    paginate_by = 10

    def get_queryset(self):
        queryset = TrainingCategory.objects.order_by('name')

        q = self.request.GET.get('q', '').strip()
        is_active = self.request.GET.get('is_active', '').strip()

        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) |
                Q(code__icontains=q)
            )

        if is_active == '1':
            queryset = queryset.filter(is_active=True)
        elif is_active == '0':
            queryset = queryset.filter(is_active=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()

        params = self.request.GET.copy()
        if 'page' in params:
            params.pop('page')

        context['filters'] = self.request.GET
        context['querystring'] = params.urlencode()
        context['training_kpis'] = [
            {'label': 'Categorías', 'value': qs.count()},
            {'label': 'Activas', 'value': qs.filter(is_active=True).count()},
            {'label': 'Inactivas', 'value': qs.filter(is_active=False).count()},
            {'label': 'Con código', 'value': qs.exclude(code='').exclude(code__isnull=True).count()},
        ]
        return context

class TrainingCategoryCreateView(LoginRequiredMixin, CreateView):
    model = TrainingCategory
    form_class = TrainingCategoryForm
    template_name = 'training/category_form.html'
    success_url = reverse_lazy('training:category_list')


class TrainingCategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = TrainingCategory
    form_class = TrainingCategoryForm
    template_name = 'training/category_form.html'
    success_url = reverse_lazy('training:category_list')


class TrainingCategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = TrainingCategory
    template_name = 'training/category_confirm_delete.html'
    success_url = reverse_lazy('training:category_list')


# =========================================================
# CURSOS
# =========================================================

class TrainingCourseListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = TrainingCourse
    template_name = 'training/course_list.html'
    context_object_name = 'courses'
    paginate_by = 10
    login_url = '/login/'
    company_field_name = 'company'

    def get_base_queryset(self):
        return TrainingCourse.objects.select_related(
            'company', 'category'
        ).prefetch_related('required_for_job_positions')

    def get_queryset(self):
        queryset = self.get_company_scoped_queryset(self.get_base_queryset())

        q = self.request.GET.get('q', '').strip()
        category = self.request.GET.get('category', '').strip()
        status = self.request.GET.get('status', '').strip()
        modality = self.request.GET.get('modality', '').strip()
        renewal = self.request.GET.get('renewal', '').strip()

        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) |
                Q(code__icontains=q) |
                Q(description__icontains=q)
            )

        if category:
            queryset = queryset.filter(category_id=category)

        if status:
            queryset = queryset.filter(status=status)

        if modality:
            queryset = queryset.filter(modality=modality)

        if renewal == '1':
            queryset = queryset.filter(requires_renewal=True)

        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        params = self.request.GET.copy()
        if 'page' in params:
            params.pop('page')

        context['filters'] = self.request.GET
        context['querystring'] = params.urlencode()
        context['categories'] = TrainingCategory.objects.order_by('name')
        context['training_kpis'] = [
            {'label': 'Cursos', 'value': qs.count()},
            {'label': 'Activos', 'value': qs.filter(status='active').count()},
            {'label': 'Con renovación', 'value': qs.filter(requires_renewal=True).count()},
            {'label': 'Obligatorios', 'value': qs.filter(is_mandatory=True).count()},
        ]
        return context


class TrainingCourseDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = TrainingCourse
    template_name = 'training/course_detail.html'
    context_object_name = 'course'
    login_url = '/login/'
    company_field_name = 'company'

    def get_queryset(self):
        return self.get_company_scoped_queryset(
            TrainingCourse.objects.select_related('company', 'category')
            .prefetch_related('required_for_job_positions')
        )


class TrainingCourseCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = TrainingCourse
    form_class = TrainingCourseForm
    template_name = 'training/course_form.html'
    success_url = reverse_lazy('training:course_list')
    login_url = '/login/'
    company_field_name = 'company'

    def form_valid(self, form):
        active_company = self.get_active_company()
        if active_company:
            form.instance.company = active_company
        return super().form_valid(form)


class TrainingCourseUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = TrainingCourse
    form_class = TrainingCourseForm
    template_name = 'training/course_form.html'
    success_url = reverse_lazy('training:course_list')
    login_url = '/login/'
    company_field_name = 'company'

    def get_queryset(self):
        return self.get_company_scoped_queryset(
            TrainingCourse.objects.select_related('company', 'category')
        )


class TrainingCourseDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = TrainingCourse
    template_name = 'training/course_confirm_delete.html'
    success_url = reverse_lazy('training:course_list')
    login_url = '/login/'
    company_field_name = 'company'

    def get_queryset(self):
        return self.get_company_scoped_queryset(
            TrainingCourse.objects.select_related('company')
        )


# =========================================================
# REGISTROS
# =========================================================

class TrainingRecordListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = TrainingRecord
    template_name = 'training/record_list.html'
    context_object_name = 'records'
    paginate_by = 10
    login_url = '/login/'
    company_field_name = 'company'

    def get_base_queryset(self):
        return TrainingRecord.objects.select_related(
            'company',
            'worker',
            'course',
        ).order_by('-completed_date', '-created_at')

    def get_queryset(self):
        queryset = self.get_company_scoped_queryset(self.get_base_queryset())

        q = self.request.GET.get('q', '').strip()
        company = self.request.GET.get('company', '').strip()
        course = self.request.GET.get('course', '').strip()
        expired = self.request.GET.get('expired', '').strip()
        expiring = self.request.GET.get('expiring', '').strip()
        status = self.request.GET.get('status', '').strip()
        expiry_state = self.request.GET.get('expiry_state', '').strip()
        today = timezone.localdate()
        next_30_days = today + timedelta(days=30)
        if expiry_state == 'expired':
            queryset = queryset.filter(
                expiry_date__isnull=False,
                expiry_date__lt=today
            )
        elif expiry_state == 'expiring':
            queryset = queryset.filter(
                expiry_date__isnull=False,
                expiry_date__gte=today,
                expiry_date__lte=next_30_days
            )
        elif expiry_state == 'valid':
            queryset = queryset.filter(
                expiry_date__isnull=False,
                expiry_date__gt=next_30_days
            )
        elif expiry_state == 'no_expiry':
            queryset = queryset.filter(expiry_date__isnull=True)
                
        if q:
            queryset = queryset.filter(
                Q(worker__first_name__icontains=q) |
                Q(worker__last_name__icontains=q) |
                Q(course__name__icontains=q) |
                Q(notes__icontains=q) |
                Q(certificate_number__icontains=q)
            )

        if company and self.request.user.is_superuser:
            queryset = queryset.filter(company_id=company)

        if course:
            queryset = queryset.filter(course_id=course)

        if status:
            queryset = queryset.filter(status=status)

        if expired == '1':
            queryset = queryset.filter(
                expiry_date__isnull=False,
                expiry_date__lt=today
            )

        if expiring == '1':
            queryset = queryset.filter(
                expiry_date__isnull=False,
                expiry_date__gte=today,
                expiry_date__lte=next_30_days
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters'] = self.request.GET

        active_company = self.get_active_company()
        qs = self.get_queryset()
        params = self.request.GET.copy()
        if 'page' in params:
            params.pop('page')

        context['querystring'] = params.urlencode()

        if self.request.user.is_superuser:
            context['companies'] = Company.objects.order_by('legal_name')
            if active_company:
                context['courses'] = TrainingCourse.objects.filter(company=active_company).order_by('name')
            else:
                context['courses'] = TrainingCourse.objects.order_by('name')
        else:
            context['companies'] = Company.objects.filter(
                id=getattr(active_company, 'id', None)
            )
            if active_company:
                context['courses'] = TrainingCourse.objects.filter(company=active_company).order_by('name')
            else:
                context['courses'] = TrainingCourse.objects.none()

        today = timezone.localdate()
        next_30_days = today + timedelta(days=30)
        context['training_kpis'] = [
            {'label': 'Registros', 'value': qs.count()},
            {'label': 'Completados', 'value': qs.filter(status='completed').count()},
            {'label': 'Caducados', 'value': qs.filter(expiry_date__isnull=False, expiry_date__lt=today).count()},
            {'label': 'Caducan pronto', 'value': qs.filter(expiry_date__isnull=False, expiry_date__gte=today, expiry_date__lte=next_30_days).count()},
        ]

    
        return context


class TrainingRecordDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = TrainingRecord
    template_name = 'training/record_detail.html'
    context_object_name = 'record'
    login_url = '/login/'
    company_field_name = 'company'

    def get_queryset(self):
        queryset = TrainingRecord.objects.select_related(
            'company',
            'worker',
            'course',
        )
        return self.get_company_scoped_queryset(queryset)


class TrainingRecordCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = TrainingRecord
    form_class = TrainingRecordForm
    template_name = 'training/record_form.html'
    success_url = reverse_lazy('training:record_list')
    login_url = '/login/'
    company_field_name = 'company'

    def form_valid(self, form):
        active_company = self.get_active_company()
        if active_company:
            form.instance.company = active_company
        if self.request.user.is_authenticated:
            form.instance.created_by = self.request.user
        return super().form_valid(form)


class TrainingRecordUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = TrainingRecord
    form_class = TrainingRecordForm
    template_name = 'training/record_form.html'
    success_url = reverse_lazy('training:record_list')
    login_url = '/login/'
    company_field_name = 'company'

    def get_queryset(self):
        return self.get_company_scoped_queryset(
            TrainingRecord.objects.select_related('company', 'worker', 'course')
        )


class TrainingRecordDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = TrainingRecord
    template_name = 'training/record_confirm_delete.html'
    success_url = reverse_lazy('training:record_list')
    login_url = '/login/'
    company_field_name = 'company'

    def get_queryset(self):
        return self.get_company_scoped_queryset(
            TrainingRecord.objects.select_related('company')
        )


class TrainingDashboardView(LoginRequiredMixin, CompanyScopedMixin, TemplateView):
    template_name = 'training/dashboard.html'
    login_url = '/login/'
    company_field_name = 'company'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = timezone.localdate()
        next_30_days = today + timedelta(days=30)

        active_company = self.get_active_company()
        is_superuser = self.request.user.is_superuser

        records = TrainingRecord.objects.select_related('company', 'worker', 'course')
        needs = TrainingNeed.objects.select_related('company', 'worker', 'course').filter(
            status__in=['pending', 'scheduled']
        )
        alerts = TrainingAlert.objects.select_related('company', 'worker', 'course').filter(
            status='open'
        )

        if not is_superuser:
            if active_company:
                records = records.filter(company=active_company)
                needs = needs.filter(company=active_company)
                alerts = alerts.filter(company=active_company)
            else:
                records = TrainingRecord.objects.none()
                needs = TrainingNeed.objects.none()
                alerts = TrainingAlert.objects.none()

        expired_records_qs = records.filter(
            expiry_date__isnull=False,
            expiry_date__lt=today
        )

        expiring_records_qs = records.filter(
            expiry_date__isnull=False,
            expiry_date__gte=today,
            expiry_date__lte=next_30_days
        )

        context['active_company'] = active_company

        context['training_kpis'] = [
            {'label': 'Registros', 'value': records.count()},
            {'label': 'Caducados', 'value': expired_records_qs.count()},
            {'label': 'Caducan pronto', 'value': expiring_records_qs.count()},
            {'label': 'Necesidades pendientes', 'value': needs.count()},
        ]

        context['expiring_records'] = expiring_records_qs.order_by('expiry_date')[:10]
        context['expired_records'] = expired_records_qs.order_by('expiry_date')[:10]
        context['pending_needs'] = needs.order_by('priority', 'due_date')[:10]
        context['open_alerts'] = alerts.order_by('due_date', '-created_at')[:10]

        return context


@login_required(login_url='/login/')
def exportar_formacion_excel(request):
    from apps.core.export import exportar_excel

    empresa = getattr(request, 'active_company', None)
    qs = TrainingRecord.objects.select_related('company', 'worker', 'course')
    if empresa:
        qs = qs.filter(company=empresa)
    else:
        qs = qs.none()

    columns = [
        {'header': 'Trabajador', 'value': lambda r: str(r.worker), 'width': 25},
        {'header': 'Empresa', 'value': lambda r: str(r.company) if r.company else '', 'width': 25},
        {'header': 'Curso', 'value': lambda r: str(r.course), 'width': 30},
        {'header': 'Estado', 'value': lambda r: r.get_status_display(), 'width': 15},
        {'header': 'Fecha Planificada', 'value': lambda r: r.planned_date.strftime('%d/%m/%Y') if r.planned_date else '', 'width': 15},
        {'header': 'Fecha Realizacion', 'value': lambda r: r.completed_date.strftime('%d/%m/%Y') if r.completed_date else '', 'width': 15},
        {'header': 'Fecha Caducidad', 'value': lambda r: r.expiry_date.strftime('%d/%m/%Y') if r.expiry_date else '', 'width': 15},
        {'header': 'Vigencia', 'value': lambda r: r.expiry_status_label, 'width': 15},
        {'header': 'Formador', 'value': lambda r: r.trainer_name or '', 'width': 20},
        {'header': 'Entidad', 'value': lambda r: r.training_entity or '', 'width': 20},
        {'header': 'Certificado', 'value': lambda r: r.certificate_number or '', 'width': 15},
        {'header': 'Asistencia %', 'value': lambda r: r.attendance_percentage if r.attendance_percentage else '', 'width': 12},
        {'header': 'Calificacion', 'value': lambda r: float(r.score) if r.score else '', 'width': 12},
    ]

    subtitle = f'Empresa: {empresa}' if empresa else 'Sin empresa activa'
    return exportar_excel(
        queryset=qs,
        columns=columns,
        title='Registros de Formacion',
        filename='formacion.xlsx',
        subtitle=subtitle,
    )