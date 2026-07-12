from datetime import timedelta
from django.utils import timezone
from .models import TrainingRequirement, TrainingNeed, TrainingAlert, TrainingRecord


def generate_training_needs_for_worker(worker):
    company = worker.company
    job_position = getattr(worker, 'job_position', None)

    if not company or not job_position:
        return 0

    requirements = TrainingRequirement.objects.filter(
        company=company,
        job_position=job_position,
        is_active=True
    ).select_related('course')

    created = 0

    for requirement in requirements:
        latest_record = TrainingRecord.objects.filter(
            company=company,
            worker=worker,
            course=requirement.course,
            status='completed'
        ).order_by('-completed_date').first()

        needs_training = False
        due_date = None

        if not latest_record:
            needs_training = True
            due_date = timezone.localdate()
        else:
            if latest_record.expiry_date and latest_record.expiry_date <= timezone.localdate() + timedelta(days=30):
                needs_training = True
                due_date = latest_record.expiry_date

        if needs_training:
            need, was_created = TrainingNeed.objects.get_or_create(
                company=company,
                worker=worker,
                course=requirement.course,
                status=TrainingNeed.STATUS_PENDING,
                defaults={
                    'job_position': job_position,
                    'requirement': requirement,
                    'due_date': due_date,
                    'priority': 1 if requirement.is_mandatory else 2,
                    'source': 'job_position',
                }
            )
            if was_created:
                created += 1

    return created

def refresh_training_alerts_for_record(record):
    if not record.company:
        return

    today = timezone.localdate()

    TrainingAlert.objects.filter(record=record, status='open').delete()

    if not record.expiry_date:
        return

    if record.expiry_date < today:
        TrainingAlert.objects.create(
            company=record.company,
            worker=record.worker,
            course=record.course,
            record=record,
            alert_type=TrainingAlert.TYPE_EXPIRED,
            title=f'Formación caducada: {record.worker} · {record.course}',
            message='El registro formativo ha superado su fecha de vigencia.',
            due_date=record.expiry_date,
        )
    elif record.expiry_date <= today + timedelta(days=30):
        TrainingAlert.objects.create(
            company=record.company,
            worker=record.worker,
            course=record.course,
            record=record,
            alert_type=TrainingAlert.TYPE_EXPIRING,
            title=f'Formación próxima a caducar: {record.worker} · {record.course}',
            message='El registro formativo caduca en los próximos 30 días.',
            due_date=record.expiry_date,
        )

    if record.status == 'completed' and not record.effectiveness_validated:
        TrainingAlert.objects.create(
            company=record.company,
            worker=record.worker,
            course=record.course,
            record=record,
            alert_type=TrainingAlert.TYPE_EFFECTIVENESS,
            title=f'Validación pendiente de eficacia: {record.worker} · {record.course}',
            message='La formación está completada, pero falta validar su eficacia.',
            due_date=record.completed_date or today,
        )