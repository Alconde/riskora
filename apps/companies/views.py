from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST

from apps.companies.forms import CompanyForm
from apps.companies.models import Company, CompanyMembership


class CompanyListView(LoginRequiredMixin, ListView):
    model = Company
    template_name = 'companies/company_list.html'
    context_object_name = 'companies'
    ordering = ['trade_name']


class CompanyDetailView(LoginRequiredMixin, DetailView):
    model = Company
    template_name = 'companies/company_detail.html'
    context_object_name = 'company'


class CompanyCreateView(LoginRequiredMixin, CreateView):
    model = Company
    form_class = CompanyForm
    template_name = 'companies/company_form.html'
    success_url = reverse_lazy('companies:company-list')


class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = 'companies/company_form.html'

    def get_success_url(self):
        return reverse_lazy('companies:company-detail', kwargs={'pk': self.object.pk})


class CompanyDeleteView(LoginRequiredMixin, DeleteView):
    model = Company
    template_name = 'companies/company_confirm_delete.html'
    success_url = reverse_lazy('companies:company-list')
    login_url = '/login/'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Empresa eliminada correctamente.')
        return super().delete(request, *args, **kwargs)


@login_required
@require_POST
def switch_company(request, company_id=None):
    if company_id is None:
        company_id = request.POST.get('company')

    if not company_id:
        return redirect('dashboard')

    if request.user.is_superuser:
        company = get_object_or_404(Company, pk=company_id)
        request.session['active_company_id'] = company.id
        return redirect('dashboard')

    membership = get_object_or_404(
        CompanyMembership,
        user=request.user,
        company_id=company_id,
        is_active=True,
        company__status=Company.Status.ACTIVE
    )

    request.session['active_company_id'] = membership.company_id
    return redirect('dashboard')