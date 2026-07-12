from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils import timezone
from django.views.generic import DetailView, ListView

from apps.companies.models import Company
from .models import Task, Alert


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 20
    login_url = '/admin/login/'

    def get_queryset(self):
        queryset = Task.objects.select_related(
            'company', 'assigned_to', 'created_by'
        ).order_by('status', 'due_date', '-created_at')

        if not self.request.user.is_superuser:
            if self.request.active_company:
                queryset = queryset.filter(company=self.request.active_company)
            else:
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
    login_url = '/admin/login/'

    def get_queryset(self):
        queryset = Task.objects.select_related(
            'company', 'assigned_to', 'created_by'
        )

        if self.request.user.is_superuser:
            return queryset

        if self.request.active_company:
            return queryset.filter(company=self.request.active_company)

        return queryset.none()


class AlertDetailView(LoginRequiredMixin, DetailView):
    model = Alert
    template_name = 'tasks/alert_detail.html'
    context_object_name = 'alert'
    login_url = '/admin/login/'

    def get_queryset(self):
        queryset = Alert.objects.select_related(
            'company', 'related_task'
        )

        if self.request.user.is_superuser:
            return queryset

        if self.request.active_company:
            return queryset.filter(company=self.request.active_company)

        return queryset.none()