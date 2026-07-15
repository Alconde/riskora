from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView

from apps.companies.models import Company
from apps.core.mixins import CompanyScopedMixin
from .forms import TaskForm
from .models import Task, Alert, mark_task_completed


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 20
    login_url = '/login/'

    def get_queryset(self):
        queryset = Task.objects.select_related(
            'company', 'assigned_to', 'created_by'
        ).order_by('status', 'due_date', '-created_at')

        active_company = getattr(self.request, 'active_company', None)
        if active_company:
            queryset = queryset.filter(company=active_company)
        elif not self.request.user.is_superuser:
            queryset = queryset.none()

        q = self.request.GET.get('q', '').strip()
        company = self.request.GET.get('company', '').strip()
        status = self.request.GET.get('status', '').strip()
        priority = self.request.GET.get('priority', '').strip()
        assigned = self.request.GET.get('assigned', '').strip()
        overdue = self.request.GET.get('overdue', '').strip()
        due_soon = self.request.GET.get('due_soon', '').strip()

        today = timezone.localdate()
        next_7_days = today + timedelta(days=7)

        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(notes__icontains=q)
            )

        if company and self.request.user.is_superuser:
            queryset = queryset.filter(company_id=company)

        if status:
            queryset = queryset.filter(status=status)

        if priority:
            queryset = queryset.filter(priority=priority)

        if assigned == '1':
            queryset = queryset.filter(assigned_to=self.request.user)

        if overdue == '1':
            queryset = queryset.filter(
                due_date__isnull=False,
                due_date__lt=today,
                status__in=[Task.Status.PENDING, Task.Status.IN_PROGRESS]
            )

        if due_soon == '1':
            queryset = queryset.filter(
                due_date__isnull=False,
                due_date__gte=today,
                due_date__lte=next_7_days,
                status__in=[Task.Status.PENDING, Task.Status.IN_PROGRESS]
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters'] = self.request.GET
        context['status_choices'] = Task.Status.choices
        context['priority_choices'] = Task.Priority.choices

        if self.request.user.is_superuser:
            context['companies'] = Company.objects.order_by('legal_name')
        else:
            context['companies'] = Company.objects.filter(
                id=getattr(self.request.active_company, 'id', None)
            )

        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'
    login_url = '/login/'

    def get_queryset(self):
        queryset = Task.objects.select_related(
            'company', 'assigned_to', 'created_by'
        )
        active_company = getattr(self.request, 'active_company', None)
        if active_company:
            return queryset.filter(company=active_company)
        if self.request.user.is_superuser:
            return queryset
        return queryset.none()


class TaskCreateView(LoginRequiredMixin, CompanyScopedMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:list')
    login_url = '/login/'
    company_field_name = 'company'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        empresa = getattr(self.request, 'active_company', None)
        kwargs['empresa'] = empresa
        if empresa and self.request.method == 'GET':
            kwargs['initial'] = {'company': empresa}
        return kwargs

    def form_valid(self, form):
        empresa = getattr(self.request, 'active_company', None)
        if empresa:
            form.instance.company = empresa
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, CompanyScopedMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    login_url = '/login/'
    company_field_name = 'company'

    def get_queryset(self):
        queryset = Task.objects.select_related('company', 'assigned_to', 'created_by')
        active_company = getattr(self.request, 'active_company', None)
        if active_company:
            return queryset.filter(company=active_company)
        if self.request.user.is_superuser:
            return queryset
        return queryset.none()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = getattr(self.request, 'active_company', None)
        return kwargs

    def get_success_url(self):
        return reverse_lazy('tasks:detail', kwargs={'pk': self.object.pk})


class TaskDeleteView(LoginRequiredMixin, CompanyScopedMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks:list')
    login_url = '/login/'
    company_field_name = 'company'

    def get_queryset(self):
        queryset = Task.objects.select_related('company')
        active_company = getattr(self.request, 'active_company', None)
        if active_company:
            return queryset.filter(company=active_company)
        if self.request.user.is_superuser:
            return queryset
        return queryset.none()

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Tarea eliminada correctamente.')
        return super().delete(request, *args, **kwargs)


class TaskCompleteView(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request, pk):
        task = Task.objects.get(pk=pk)
        mark_task_completed(task)
        messages.success(request, 'Tarea marcada como completada.')
        return HttpResponseRedirect(reverse_lazy('tasks:detail', kwargs={'pk': pk}))


# =========================================================
# ALERTAS
# =========================================================


class AlertListView(LoginRequiredMixin, ListView):
    model = Alert
    template_name = 'tasks/alert_list.html'
    context_object_name = 'alerts'
    paginate_by = 20
    login_url = '/login/'

    def get_queryset(self):
        queryset = Alert.objects.select_related(
            'company', 'related_task'
        )

        active_company = getattr(self.request, 'active_company', None)
        if active_company:
            queryset = queryset.filter(company=active_company)
        elif not self.request.user.is_superuser:
            queryset = queryset.none()

        q = self.request.GET.get('q', '').strip()
        alert_type = self.request.GET.get('alert_type', '').strip()
        severity = self.request.GET.get('severity', '').strip()
        status = self.request.GET.get('status', '').strip()

        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(message__icontains=q)
            )

        if alert_type:
            queryset = queryset.filter(alert_type=alert_type)

        if severity:
            queryset = queryset.filter(severity=severity)

        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        elif status == 'unread':
            queryset = queryset.filter(is_active=True, is_read=False)

        return queryset.order_by('-is_active', 'due_date', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters'] = self.request.GET
        context['alert_type_choices'] = Alert.AlertType.choices
        context['severity_choices'] = Alert.Severity.choices
        context['status_choices'] = [
            ('active', 'Activas'),
            ('inactive', 'Cerradas'),
            ('unread', 'Sin leer'),
        ]

        active_company = getattr(self.request, 'active_company', None)
        if self.request.user.is_superuser:
            context['companies'] = Company.objects.order_by('legal_name')
        else:
            context['companies'] = Company.objects.filter(
                id=getattr(active_company, 'id', None)
            )

        return context


class AlertDetailView(LoginRequiredMixin, DetailView):
    model = Alert
    template_name = 'tasks/alert_detail.html'
    context_object_name = 'alert'
    login_url = '/login/'

    def get_queryset(self):
        queryset = Alert.objects.select_related(
            'company', 'related_task'
        )
        active_company = getattr(self.request, 'active_company', None)
        if active_company:
            return queryset.filter(company=active_company)
        if self.request.user.is_superuser:
            return queryset
        return queryset.none()

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.is_read:
            obj.is_read = True
            obj.read_at = timezone.now()
            obj.save(update_fields=['is_read', 'read_at', 'updated_at'])
        return obj


class AlertDismissView(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request, pk):
        alert = Alert.objects.get(pk=pk)
        alert.is_active = False
        alert.is_read = True
        alert.read_at = timezone.now()
        alert.save(update_fields=['is_active', 'is_read', 'read_at', 'updated_at'])
        messages.success(request, 'Alerta cerrada correctamente.')
        return HttpResponseRedirect(reverse_lazy('tasks:alert-list'))
