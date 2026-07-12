from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import Q

from apps.workcenters.forms import WorkCenterForm
from apps.workcenters.models import WorkCenter
from apps.companies.models import Company
from apps.core.mixins import CompanyScopedMixin


class WorkCenterListView(LoginRequiredMixin, CompanyScopedMixin, ListView):
    model = WorkCenter
    template_name = 'workcenters/workcenter_list.html'
    context_object_name = 'workcenters'
    paginate_by = 20
    login_url = '/admin/login/'
    company_field_name = 'company'

    def get_base_queryset(self):
        return WorkCenter.objects.select_related('company').order_by('name')

    def get_queryset(self):
        queryset = self.get_company_scoped_queryset(self.get_base_queryset())

        q = self.request.GET.get('q', '').strip()
        company = self.request.GET.get('company', '').strip()
        status = self.request.GET.get('status', '').strip()
        province = self.request.GET.get('province', '').strip()

        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) |
                Q(code__icontains=q) |
                Q(address__icontains=q) |
                Q(city__icontains=q)
            )

        if company and self.request.user.is_superuser:
            queryset = queryset.filter(company_id=company)

        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)

        if province:
            queryset = queryset.filter(province__icontains=province)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters'] = self.request.GET
        context['status_choices'] = [
            ('active', 'Activos'),
            ('inactive', 'Inactivos'),
        ]
        context['risk_level_choices'] = WorkCenter.RiskLevel.choices

        active_company = self.get_active_company()

        if self.request.user.is_superuser:
            context['companies'] = Company.objects.order_by('legal_name')
        else:
            context['companies'] = Company.objects.filter(
                id=getattr(active_company, 'id', None)
            )

        return context


class WorkCenterDetailView(LoginRequiredMixin, CompanyScopedMixin, DetailView):
    model = WorkCenter
    template_name = 'workcenters/workcenter_detail.html'
    context_object_name = 'workcenter'
    login_url = '/admin/login/'
    company_field_name = 'company'

    def get_queryset(self):
        queryset = WorkCenter.objects.select_related('company')
        return self.get_company_scoped_queryset(queryset)


class WorkCenterCreateView(LoginRequiredMixin, CreateView):
    model = WorkCenter
    form_class = WorkCenterForm
    template_name = 'workcenters/workcenter_form.html'
    success_url = reverse_lazy('workcenter-list')


class WorkCenterUpdateView(LoginRequiredMixin, UpdateView):
    model = WorkCenter
    form_class = WorkCenterForm
    template_name = 'workcenters/workcenter_form.html'

    def get_success_url(self):
        return reverse_lazy('workcenter-detail', kwargs={'pk': self.object.pk})