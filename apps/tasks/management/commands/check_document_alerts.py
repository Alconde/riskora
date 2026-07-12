from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.documents.models import Document
from apps.tasks.models import Alert, Task


class Command(BaseCommand):
    help = 'Genera alertas para documentos caducados o próximos a caducar.'

    def handle(self, *args, **options):
        today = timezone.localdate()
        warning_days = 30

        expired_count = 0
        warning_count = 0
        task_count = 0

        document_content_type = ContentType.objects.get_for_model(Document)

        documents = Document.objects.filter(
            expiry_date__isnull=False
        ).exclude(
            status__in=['revoked', 'archived']
        ).select_related('company', 'category')

        for document in documents:
            if document.expiry_date <= today:
                with transaction.atomic():
                    alert, created = Alert.objects.get_or_create(
                        company=document.company,
                        alert_type=Alert.AlertType.DOCUMENT_EXPIRY,
                        content_type=document_content_type,
                        object_id=str(document.pk),
                        title=f'Documento caducado: {document.title}',
                        defaults={
                            'message': f'El documento "{document.title}" ha caducado el {document.expiry_date}.',
                            'severity': Alert.Severity.DANGER,
                            'due_date': document.expiry_date,
                            'is_active': True,
                        }
                    )

                    if created:
                        expired_count += 1

                    task, task_created = Task.objects.get_or_create(
                        company=document.company,
                        content_type=document_content_type,
                        object_id=str(document.pk),
                        title=f'Revisar documento caducado: {document.title}',
                        defaults={
                            'description': (
                                f'El documento "{document.title}" de la categoría '
                                f'"{document.category.name}" ha caducado y requiere revisión.'
                            ),
                            'status': Task.Status.PENDING,
                            'priority': Task.Priority.HIGH,
                            'due_date': today,
                        }
                    )

                    if task_created:
                        task_count += 1

                    if alert.related_task_id != task.id:
                        alert.related_task = task
                        alert.save(update_fields=['related_task', 'updated_at'])

            elif document.expiry_date <= today + timedelta(days=warning_days):
                _, created = Alert.objects.get_or_create(
                    company=document.company,
                    alert_type=Alert.AlertType.DOCUMENT_EXPIRY,
                    content_type=document_content_type,
                    object_id=str(document.pk),
                    title=f'Documento próximo a caducar: {document.title}',
                    defaults={
                        'message': f'El documento "{document.title}" caduca el {document.expiry_date}.',
                        'severity': Alert.Severity.WARNING,
                        'due_date': document.expiry_date,
                        'is_active': True,
                    }
                )

                if created:
                    warning_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Proceso completado. '
                f'Alertas de caducados creadas: {expired_count}. '
                f'Alertas de aviso creadas: {warning_count}. '
                f'Tareas creadas: {task_count}.'
            )
        )