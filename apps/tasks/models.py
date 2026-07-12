from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone


class Task(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        IN_PROGRESS = 'in_progress', 'En progreso'
        COMPLETED = 'completed', 'Completada'
        CANCELLED = 'cancelled', 'Cancelada'

    class Priority(models.TextChoices):
        LOW = 'low', 'Baja'
        MEDIUM = 'medium', 'Media'
        HIGH = 'high', 'Alta'
        CRITICAL = 'critical', 'Crítica'

    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='empresa'
    )
    title = models.CharField('título', max_length=255)
    description = models.TextField('descripción', blank=True)

    status = models.CharField(
        'estado',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    priority = models.CharField(
        'prioridad',
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name='asignada a'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_tasks',
        verbose_name='creada por'
    )

    due_date = models.DateField('fecha límite', null=True, blank=True)
    completed_at = models.DateTimeField('completada el', null=True, blank=True)

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='tipo de objeto'
    )
    object_id = models.CharField(
        max_length=36,
        null=True,
        blank=True,
        verbose_name='id del objeto'
    )
    content_object = GenericForeignKey('content_type', 'object_id')

    notes = models.TextField('observaciones', blank=True)

    created_at = models.DateTimeField('creada el', auto_now_add=True)
    updated_at = models.DateTimeField('actualizada el', auto_now=True)

    class Meta:
        verbose_name = 'tarea'
        verbose_name_plural = 'tareas'
        ordering = ['status', 'due_date', '-created_at']
        indexes = [
            models.Index(fields=['company', 'status']),
            models.Index(fields=['company', 'due_date']),
            models.Index(fields=['priority', 'status']),
        ]

    def __str__(self):
        return self.title


class Alert(models.Model):
    class AlertType(models.TextChoices):
        DOCUMENT_EXPIRY = 'document_expiry', 'Caducidad documental'
        DOCUMENT_REVIEW = 'document_review', 'Revisión documental'
        TRAINING_EXPIRY = 'training_expiry', 'Caducidad de formación'
        HEALTH_SURVEILLANCE = 'health_surveillance', 'Vigilancia de la salud'
        GENERIC = 'generic', 'Genérica'

    class Severity(models.TextChoices):
        INFO = 'info', 'Info'
        WARNING = 'warning', 'Aviso'
        DANGER = 'danger', 'Crítica'

    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='alerts',
        verbose_name='empresa'
    )

    title = models.CharField('título', max_length=255)
    message = models.TextField('mensaje')
    alert_type = models.CharField(
        'tipo de alerta',
        max_length=30,
        choices=AlertType.choices,
        default=AlertType.GENERIC
    )
    severity = models.CharField(
        'criticidad',
        max_length=20,
        choices=Severity.choices,
        default=Severity.WARNING
    )

    due_date = models.DateField('fecha objetivo', null=True, blank=True)
    is_active = models.BooleanField('activa', default=True)
    is_read = models.BooleanField('leída', default=False)
    read_at = models.DateTimeField('leída el', null=True, blank=True)

    related_task = models.ForeignKey(
        'tasks.Task',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alerts',
        verbose_name='tarea relacionada'
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='tipo de objeto'
    )
    object_id = models.CharField(
        max_length=36,
        null=True,
        blank=True,
        verbose_name='id del objeto'
    )
    content_object = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField('creada el', auto_now_add=True)
    updated_at = models.DateTimeField('actualizada el', auto_now=True)

    class Meta:
        verbose_name = 'alerta'
        verbose_name_plural = 'alertas'
        ordering = ['-is_active', 'due_date', '-created_at']
        indexes = [
            models.Index(fields=['company', 'is_active']),
            models.Index(fields=['alert_type', 'severity']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return self.title
    
def mark_task_completed(task):
    task.status = Task.Status.COMPLETED
    task.completed_at = timezone.now()
    task.save(update_fields=['status', 'completed_at', 'updated_at'])
