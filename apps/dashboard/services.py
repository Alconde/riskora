from datetime import timedelta
from django.utils import timezone

from apps.companies.models import Company
from apps.documents.models import Document
from apps.tasks.models import Task, Alert
from apps.training.models import TrainingRecord
from apps.workcenters.models import WorkCenter
from apps.workers.models import Worker, JobPosition


def build_dashboard_context(active_company=None, is_superuser=False):
    today = timezone.localdate()
    next_30_days = today + timedelta(days=30)

    companies_qs = Company.objects.all().order_by('legal_name')
    workcenters_qs = WorkCenter.objects.select_related('company')
    workers_qs = Worker.objects.select_related('company', 'work_center', 'job_position')
    positions_qs = JobPosition.objects.select_related('company')
    documents_qs = Document.objects.select_related('company', 'category', 'uploaded_by')
    tasks_qs = Task.objects.select_related('company', 'assigned_to', 'created_by')
    alerts_qs = Alert.objects.select_related('company', 'related_task')
    training_qs = TrainingRecord.objects.select_related('company', 'worker', 'course')

    if not is_superuser:
        if active_company:
            companies_qs = companies_qs.filter(pk=active_company.pk)
            workcenters_qs = workcenters_qs.filter(company=active_company)
            workers_qs = workers_qs.filter(company=active_company)
            positions_qs = positions_qs.filter(company=active_company)
            documents_qs = documents_qs.filter(company=active_company)
            tasks_qs = tasks_qs.filter(company=active_company)
            alerts_qs = alerts_qs.filter(company=active_company)
            training_qs = training_qs.filter(company=active_company)
        else:
            companies_qs = Company.objects.none()
            workcenters_qs = WorkCenter.objects.none()
            workers_qs = Worker.objects.none()
            positions_qs = JobPosition.objects.none()
            documents_qs = Document.objects.none()
            tasks_qs = Task.objects.none()
            alerts_qs = Alert.objects.none()
            training_qs = TrainingRecord.objects.none()

    expired_documents_qs = documents_qs.filter(
        expiry_date__isnull=False,
        expiry_date__lt=today
    )

    expiring_documents_qs = documents_qs.filter(
        expiry_date__isnull=False,
        expiry_date__gte=today,
        expiry_date__lte=next_30_days
    )

    expiring_training_qs = training_qs.filter(
        expiry_date__isnull=False,
        expiry_date__gte=today,
        expiry_date__lte=next_30_days
    )

    pending_tasks_qs = tasks_qs.filter(status__in=['pending', 'in_progress'])
    high_priority_tasks_qs = pending_tasks_qs.filter(priority__in=['high', 'critical'])
    active_alerts_qs = alerts_qs.filter(is_active=True)

    total_companies = companies_qs.count()
    total_workcenters = workcenters_qs.count()
    total_positions = positions_qs.count()
    total_workers = workers_qs.count()
    total_documents = documents_qs.count()

    valid_documents_count = documents_qs.filter(status=Document.Status.VALID).count()
    completed_tasks_count = tasks_qs.filter(status=Task.Status.COMPLETED).count()
    valid_training_count = training_qs.filter(
        expiry_date__isnull=False,
        expiry_date__gte=today
    ).count()

    total_training = training_qs.count()
    total_actions = tasks_qs.count()

    return {
        'active_company': active_company,
        'total_companies': total_companies,
        'total_workcenters': total_workcenters,
        'total_positions': total_positions,
        'total_workers': total_workers,
        'total_documents': total_documents,
        'expired_documents': expired_documents_qs.count(),
        'active_alerts': active_alerts_qs.count(),
        'pending_tasks': pending_tasks_qs.count(),
        'high_priority_tasks': high_priority_tasks_qs.count(),
        'expiring_documents': expiring_documents_qs.order_by('expiry_date')[:5],
        'expiring_training_records': expiring_training_qs.order_by('expiry_date')[:5],
        'recent_alerts': active_alerts_qs.order_by('-created_at')[:5],
        'urgent_tasks': high_priority_tasks_qs.order_by('due_date', '-created_at')[:5],
        'recent_tasks': tasks_qs.order_by('-created_at')[:5],
        'recent_documents': documents_qs.order_by('-created_at')[:5],
        'recent_workcenters': workcenters_qs.order_by('-created_at')[:5],
        'recent_workers': workers_qs.order_by('-created_at')[:5],
        'compliance_documents': f"{round((valid_documents_count / total_documents) * 100)}%" if total_documents else "0%",
        'compliance_training': f"{round((valid_training_count / total_training) * 100)}%" if total_training else "0%",
        'compliance_actions': f"{round((completed_tasks_count / total_actions) * 100)}%" if total_actions else "0%",
    }