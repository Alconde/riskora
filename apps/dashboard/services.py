from datetime import timedelta
from django.utils import timezone

from apps.companies.models import Company
from apps.documents.models import Document
from apps.tasks.models import Task, Alert
from apps.training.models import TrainingRecord
from apps.workcenters.models import WorkCenter
from apps.workers.models import Worker, JobPosition
from apps.risk_assessment.models import EvaluacionRiesgos
from apps.corrective_actions.models import NoConformidad
from apps.inspections.models import Inspeccion
from apps.incidents.models import Accidente, Incidente
from apps.epis.models import EPI
from apps.work_equipment.models import EquipoTrabajo


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
    evaluaciones_qs = EvaluacionRiesgos.objects.select_related('empresa', 'centro_trabajo')
    nc_qs = NoConformidad.objects.select_related('empresa')
    inspecciones_qs = Inspeccion.objects.select_related('empresa', 'centro_trabajo')
    accidentes_qs = Accidente.objects.select_related('empresa', 'centro_trabajo')
    incidentes_qs = Incidente.objects.select_related('empresa', 'centro_trabajo')
    epis_qs = EPI.objects.select_related('empresa', 'catalogo')
    equipos_qs = EquipoTrabajo.objects.select_related('empresa', 'tipo')

    if active_company:
        companies_qs = companies_qs.filter(pk=active_company.pk)
        workcenters_qs = workcenters_qs.filter(company=active_company)
        workers_qs = workers_qs.filter(company=active_company)
        positions_qs = positions_qs.filter(company=active_company)
        documents_qs = documents_qs.filter(company=active_company)
        tasks_qs = tasks_qs.filter(company=active_company)
        alerts_qs = alerts_qs.filter(company=active_company)
        training_qs = training_qs.filter(company=active_company)
        evaluaciones_qs = evaluaciones_qs.filter(empresa=active_company)
        nc_qs = nc_qs.filter(empresa=active_company)
        inspecciones_qs = inspecciones_qs.filter(empresa=active_company)
        accidentes_qs = accidentes_qs.filter(empresa=active_company)
        incidentes_qs = incidentes_qs.filter(empresa=active_company)
        epis_qs = epis_qs.filter(empresa=active_company)
        equipos_qs = equipos_qs.filter(empresa=active_company)
    elif not is_superuser:
        companies_qs = Company.objects.none()
        workcenters_qs = WorkCenter.objects.none()
        workers_qs = Worker.objects.none()
        positions_qs = JobPosition.objects.none()
        documents_qs = Document.objects.none()
        tasks_qs = Task.objects.none()
        alerts_qs = Alert.objects.none()
        training_qs = TrainingRecord.objects.none()
        evaluaciones_qs = EvaluacionRiesgos.objects.none()
        nc_qs = NoConformidad.objects.none()
        inspecciones_qs = Inspeccion.objects.none()
        accidentes_qs = Accidente.objects.none()
        incidentes_qs = Incidente.objects.none()
        epis_qs = EPI.objects.none()
        equipos_qs = EquipoTrabajo.objects.none()

    # Counts
    total_workers = workers_qs.count()
    total_workcenters = workcenters_qs.count()
    total_documents = documents_qs.count()
    total_training = training_qs.count()
    total_tasks = tasks_qs.count()
    total_nc = nc_qs.count()
    total_inspecciones = inspecciones_qs.count()
    total_accidentes = accidentes_qs.count()
    total_incidentes = incidentes_qs.count()
    total_epis = epis_qs.count()
    total_equipos = equipos_qs.count()
    total_evaluaciones = evaluaciones_qs.count()

    # Alerts & pending items
    active_alerts = alerts_qs.filter(is_active=True).count()
    pending_tasks = tasks_qs.filter(status__in=['pending', 'in_progress']).count()
    high_priority_tasks = tasks_qs.filter(
        status__in=['pending', 'in_progress'],
        priority__in=['high', 'critical']
    ).count()

    # Expiring items
    expired_documents = documents_qs.filter(
        expiry_date__isnull=False, expiry_date__lt=today
    ).count()
    expiring_documents = documents_qs.filter(
        expiry_date__isnull=False, expiry_date__gte=today, expiry_date__lte=next_30_days
    ).order_by('expiry_date')[:5]

    expiring_training = training_qs.filter(
        expiry_date__isnull=False, expiry_date__gte=today, expiry_date__lte=next_30_days
    ).order_by('expiry_date')[:5]

    # Open items
    open_nc = nc_qs.filter(estado__in=['abierta', 'en_seguimiento']).count()
    inspecciones_pendientes = inspecciones_qs.filter(
        estado__in=['planificada', 'en_curso']
    ).count()
    accidentes_abiertos = accidentes_qs.filter(estado='abierto').count()
    equipos_mantenimiento = equipos_qs.filter(estado='en_mantenimiento').count()

    # Compliance
    valid_docs = documents_qs.filter(status=Document.Status.VALID).count()
    valid_training = training_qs.filter(
        expiry_date__isnull=False, expiry_date__gte=today
    ).count()
    closed_tasks = tasks_qs.filter(status=Task.Status.COMPLETED).count()

    compliance_documents = round((valid_docs / total_documents) * 100) if total_documents else 0
    compliance_training = round((valid_training / total_training) * 100) if total_training else 0
    compliance_actions = round((closed_tasks / total_tasks) * 100) if total_tasks else 0

    # Urgent alerts list
    urgent_tasks_list = tasks_qs.filter(
        status__in=['pending', 'in_progress'],
        priority__in=['high', 'critical']
    ).order_by('due_date', '-created_at')[:5]

    recent_alerts_list = alerts_qs.filter(is_active=True).order_by('-created_at')[:5]

    return {
        'active_company': active_company,
        'total_workers': total_workers,
        'total_workcenters': total_workcenters,
        'total_documents': total_documents,
        'active_alerts': active_alerts,
        'pending_tasks': pending_tasks,
        'high_priority_tasks': high_priority_tasks,
        'expired_documents': expired_documents,
        'expiring_documents': expiring_documents,
        'expiring_training_records': expiring_training,
        'total_nc': total_nc,
        'open_nc': open_nc,
        'total_inspecciones': total_inspecciones,
        'inspecciones_pendientes': inspecciones_pendientes,
        'total_accidentes': total_accidentes,
        'accidentes_abiertos': accidentes_abiertos,
        'total_incidentes': total_incidentes,
        'total_epis': total_epis,
        'total_equipos': total_equipos,
        'equipos_mantenimiento': equipos_mantenimiento,
        'total_evaluaciones': total_evaluaciones,
        'compliance_documents': compliance_documents,
        'compliance_training': compliance_training,
        'compliance_actions': compliance_actions,
        'urgent_tasks': urgent_tasks_list,
        'recent_alerts': recent_alerts_list,
    }
