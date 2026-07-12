from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils import timezone
from apps.companies.models import Company
from .models import Document, DocumentCategory
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from .forms import DocumentForm

class DocumentListView(LoginRequiredMixin, ListView):
    model = Document
    template_name = 'documents/document_list.html'
    context_object_name = 'documents'
    paginate_by = 20
    login_url = '/login/'

    def get_queryset(self):
        queryset = Document.objects.select_related(
            'company', 'category', 'uploaded_by'
        ).order_by('-created_at')

        if not self.request.user.is_superuser:
            if self.request.active_company:
                queryset = queryset.filter(company=self.request.active_company)
            else:
                queryset = queryset.none()

        q = self.request.GET.get('q', '').strip()
        company = self.request.GET.get('company', '').strip()
        status = self.request.GET.get('status', '').strip()
        category = self.request.GET.get('category', '').strip()
        expired = self.request.GET.get('expired', '').strip()
        expiring = self.request.GET.get('expiring', '').strip()
        confidential = self.request.GET.get('confidential', '').strip()

        today = timezone.localdate()
        next_30_days = today + timedelta(days=30)

        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(code__icontains=q) |
                Q(notes__icontains=q)
            )

        if company and self.request.user.is_superuser:
            queryset = queryset.filter(company_id=company)

        if status:
            queryset = queryset.filter(status=status)

        if category:
            queryset = queryset.filter(category_id=category)

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

        if confidential == '1':
            queryset = queryset.filter(is_confidential=True)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        queryset = self.object_list
        today = timezone.localdate()
        next_30_days = today + timedelta(days=30)

        context['filters'] = self.request.GET
        context['status_choices'] = Document.Status.choices
        context['today'] = today

        if self.request.user.is_superuser:
            context['companies'] = Company.objects.order_by('legal_name')
        else:
            context['companies'] = Company.objects.filter(
                id=getattr(self.request.active_company, 'id', None)
            )

        context['categories'] = DocumentCategory.objects.filter(
            is_active=True
        ).order_by('name')

        context['documents_total'] = queryset.count()
        context['documents_valid'] = queryset.filter(
            status=Document.Status.VALID
        ).count()
        context['documents_expired'] = queryset.filter(
            expiry_date__isnull=False,
            expiry_date__lt=today
        ).count()
        context['documents_expiring'] = queryset.filter(
            expiry_date__isnull=False,
            expiry_date__gte=today,
            expiry_date__lte=next_30_days
        ).count()
        context['documents_confidential'] = queryset.filter(
            is_confidential=True
        ).count()

        querydict = self.request.GET.copy()
        if 'page' in querydict:
            querydict.pop('page')
        context['querystring'] = querydict.urlencode()

        return context


class DocumentDetailView(LoginRequiredMixin, DetailView):
    model = Document
    template_name = 'documents/document_detail.html'
    context_object_name = 'document'
    login_url = '/login/'

    def get_queryset(self):
        queryset = Document.objects.select_related(
            'company', 'category', 'uploaded_by', 'content_type'
        )

        if self.request.user.is_superuser:
            return queryset

        if self.request.active_company:
            return queryset.filter(company=self.request.active_company)

        return queryset.none()
    
class DocumentCreateView(LoginRequiredMixin, CreateView):
    model = Document
    form_class = DocumentForm
    template_name = 'documents/document_form.html'
    login_url = '/login/'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        if not self.request.user.is_superuser:
            if self.request.active_company:
                form.fields['company'].queryset = Company.objects.filter(
                    pk=self.request.active_company.pk
                )
                form.fields['company'].initial = self.request.active_company
            else:
                form.fields['company'].queryset = Company.objects.none()

        form.fields['category'].queryset = DocumentCategory.objects.filter(
            is_active=True
        ).order_by('name')

        return form

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user

        if not self.request.user.is_superuser and self.request.active_company:
            form.instance.company = self.request.active_company

        messages.success(self.request, 'Documento creado correctamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('documents:detail', kwargs={'pk': self.object.pk})


class DocumentUpdateView(LoginRequiredMixin, UpdateView):
    model = Document
    form_class = DocumentForm
    template_name = 'documents/document_form.html'
    login_url = '/login/'

    def get_queryset(self):
        queryset = Document.objects.select_related(
            'company', 'category', 'uploaded_by', 'content_type'
        )

        if self.request.user.is_superuser:
            return queryset

        if self.request.active_company:
            return queryset.filter(company=self.request.active_company)

        return queryset.none()

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        if not self.request.user.is_superuser:
            if self.request.active_company:
                form.fields['company'].queryset = Company.objects.filter(
                    pk=self.request.active_company.pk
                )
            else:
                form.fields['company'].queryset = Company.objects.none()

        form.fields['category'].queryset = DocumentCategory.objects.filter(
            is_active=True
        ).order_by('name')

        return form

    def form_valid(self, form):
        messages.success(self.request, 'Documento actualizado correctamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('documents:detail', kwargs={'pk': self.object.pk})


class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    model = Document
    template_name = 'documents/document_confirm_delete.html'
    context_object_name = 'document'
    success_url = reverse_lazy('documents:list')
    login_url = '/login/'

    def get_queryset(self):
        queryset = Document.objects.select_related(
            'company', 'category', 'uploaded_by'
        )

        if self.request.user.is_superuser:
            return queryset

        if self.request.active_company:
            return queryset.filter(company=self.request.active_company)

        return queryset.none()

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Documento eliminado correctamente.')
        return super().delete(request, *args, **kwargs)