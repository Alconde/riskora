from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView

from apps.companies.models import Company
from apps.documents.models import Document
from apps.tasks.models import Task, Alert
from apps.training.models import TrainingRecord
from apps.workers.models import Worker, JobPosition
from apps.workcenters.models import WorkCenter


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    login_url = '/admin/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = timezone.localdate()
        next_30_days = today + timedelta(days=30)

        active_company = getattr(self.request, 'active_company', None)
        is_superuser = self.request.user.is_superuser

        companies_qs = Company.objects.all()
        workcenters_qs = WorkCenter.objects.select_related('company')
        positions_qs = JobPosition.objects.select_related('company')
        workers_qs = Worker.objects.select_related('company', 'work_center', 'job_position')
        documents_qs = Document.objects.select_related('company', 'category', 'uploaded_by')
        documents_total = documents_qs.count()

        documents_valid = documents_qs.filter(
            status=Document.Status.VALID
        ).count()

        documents_expired = documents_qs.filter(
            expiry_date__isnull=False,
            expiry_date__lt=today
        ).count()

        documents_expiring = documents_qs.filter(
            expiry_date__isnull=False,
            expiry_date__gte=today,
            expiry_date__lte=next_30_days
        ).count()

        documents_confidential = documents_qs.filter(
            is_confidential=True
        ).count()

        recent_documents = documents_qs.order_by('-created_at')[:5]
        tasks_qs = Task.objects.select_related('company', 'assigned_to', 'created_by')
        alerts_qs = Alert.objects.select_related('company', 'related_task')
        training_qs = TrainingRecord.objects.select_related('company', 'worker', 'course')

        if not is_superuser:
            if active_company:
                companies_qs = companies_qs.filter(id=active_company.id)
                workcenters_qs = workcenters_qs.filter(company=active_company)
                positions_qs = positions_qs.filter(company=active_company)
                workers_qs = workers_qs.filter(company=active_company)
                documents_qs = documents_qs.filter(company=active_company)
                tasks_qs = tasks_qs.filter(company=active_company)
                alerts_qs = alerts_qs.filter(company=active_company)
                training_qs = training_qs.filter(company=active_company)
            else:
                companies_qs = companies_qs.none()
                workcenters_qs = workcenters_qs.none()
                positions_qs = positions_qs.none()
                workers_qs = workers_qs.none()
                documents_qs = documents_qs.none()
                tasks_qs = tasks_qs.none()
                alerts_qs = alerts_qs.none()
                training_qs = training_qs.none()

        total_companies = companies_qs.count()
        total_workcenters = workcenters_qs.count()
        total_positions = positions_qs.count()
        total_workers = workers_qs.count()
        total_documents = documents_qs.count()

        expired_documents = documents_qs.filter(
            expiry_date__isnull=False,
            expiry_date__lt=today
        ).count()

        active_alerts = alerts_qs.filter(is_active=True).count()

        pending_tasks = tasks_qs.filter(
            status__in=[Task.Status.PENDING, Task.Status.IN_PROGRESS]
        ).count()

        high_priority_tasks = tasks_qs.filter(
            status__in=[Task.Status.PENDING, Task.Status.IN_PROGRESS],
            priority__in=[Task.Priority.HIGH, Task.Priority.CRITICAL]
        ).count()

        expiring_documents = documents_qs.filter(
            expiry_date__isnull=False,
            expiry_date__gte=today,
            expiry_date__lte=next_30_days
        ).order_by('expiry_date')[:5]

        expiring_training_records = training_qs.filter(
            expiry_date__isnull=False,
            expiry_date__gte=today,
            expiry_date__lte=next_30_days
        ).order_by('expiry_date')[:5]

        recent_alerts = alerts_qs.order_by('-created_at')[:5]

        urgent_tasks = tasks_qs.filter(
            status__in=[Task.Status.PENDING, Task.Status.IN_PROGRESS],
            priority__in=[Task.Priority.HIGH, Task.Priority.CRITICAL]
        ).order_by('due_date', '-created_at')[:5]

        recent_tasks = tasks_qs.order_by('-created_at')[:5]
        recent_documents = documents_qs.order_by('-created_at')[:5]
        recent_workcenters = workcenters_qs.order_by('-created_at')[:5]
        recent_workers = workers_qs.order_by('-created_at')[:5]

        valid_documents_count = documents_qs.filter(status=Document.Status.VALID).count()
        completed_tasks_count = tasks_qs.filter(status=Task.Status.COMPLETED).count()
        valid_training_count = training_qs.filter(
            expiry_date__isnull=False,
            expiry_date__gte=today
        ).count()

        total_training = training_qs.count()
        total_actions = tasks_qs.count()

        compliance_documents = (
            f"{round((valid_documents_count / total_documents) * 100)}%"
            if total_documents else "0%"
        )

        compliance_training = (
            f"{round((valid_training_count / total_training) * 100)}%"
            if total_training else "0%"
        )

        compliance_actions = (
            f"{round((completed_tasks_count / total_actions) * 100)}%"
            if total_actions else "0%"
        )
        
        documents_valid = documents_qs.filter(
            status=Document.Status.VALID
        ).count()

        documents_confidential = documents_qs.filter(
            is_confidential=True
        ).count()

        expiring_documents = documents_qs.filter(
            expiry_date__isnull=False,
            expiry_date__gte=today,
            expiry_date__lte=next_30_days
        ).order_by('expiry_date')[:5]


        context.update({
            'active_company': active_company,
            'documents_valid': documents_valid,
            'documents_confidential': documents_confidential,

            'total_companies': total_companies,
            'total_workcenters': total_workcenters,
            'total_positions': total_positions,
            'total_workers': total_workers,
            'total_documents': total_documents,
            'expired_documents': expired_documents,
            'active_alerts': active_alerts,
            'pending_tasks': pending_tasks,
            'high_priority_tasks': high_priority_tasks,

            'expiring_documents': expiring_documents,
            'expiring_training_records': expiring_training_records,
            'recent_alerts': recent_alerts,
            'urgent_tasks': urgent_tasks,
            'recent_tasks': recent_tasks,
            'recent_documents': recent_documents,
            'recent_workcenters': recent_workcenters,
            'recent_workers': recent_workers,

            'compliance_documents': compliance_documents,
            'compliance_training': compliance_training,
            'compliance_actions': compliance_actions,
            
        })

        return context