import uuid

from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """
    Registro inmutable de acciones sobre datos del sistema.
    Append-only: ningún registro puede modificarse ni eliminarse.
    """

    class Origin(models.TextChoices):
        USER = 'USER', 'Usuario'
        SYSTEM = 'SYSTEM', 'Sistema'
        API = 'API', 'API REST'
        IMPORT = 'IMPORT', 'Importación'
        AI = 'AI', 'Inteligencia Artificial'
        SCHEDULED_TASK = 'SCHEDULED_TASK', 'Tarea programada'

    class Action(models.TextChoices):
        CREATE = 'create', 'Creación'
        UPDATE = 'update', 'Actualización'
        DELETE = 'delete', 'Eliminación'
        LOGIN = 'login', 'Inicio de sesión'
        LOGOUT = 'logout', 'Cierre de sesión'
        EXPORT = 'export', 'Exportación'
        IMPORT_DATA = 'import_data', 'Importación de datos'
        APPROVE = 'approve', 'Aprobación'

    request_id = models.UUIDField(
        'request ID',
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )
    trace_id = models.UUIDField(
        'trace ID',
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )
    parent_event_id = models.UUIDField(
        'evento padre',
        null=True,
        blank=True,
        db_index=True,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name='usuario',
    )
    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name='empresa',
    )
    origin = models.CharField(
        'origen',
        max_length=20,
        choices=Origin.choices,
        default=Origin.USER,
    )
    ip_address = models.GenericIPAddressField(
        'dirección IP',
        null=True,
        blank=True,
    )
    user_agent = models.CharField(
        'user agent',
        max_length=500,
        blank=True,
        default='',
    )

    action = models.CharField(
        'acción',
        max_length=20,
        choices=Action.choices,
    )
    model_name = models.CharField(
        'modelo',
        max_length=100,
        help_text='Nombre del modelo Django afectado.',
    )
    object_id = models.CharField(
        'ID del objeto',
        max_length=50,
        blank=True,
        default='',
    )
    object_repr = models.CharField(
        'representación del objeto',
        max_length=300,
        blank=True,
        default='',
    )

    changes = models.JSONField(
        'cambios',
        default=dict,
        blank=True,
        help_text='JSON con los campos modificados: {campo: [antes, después]}',
    )

    timestamp = models.DateTimeField(
        'fecha y hora',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'registro de auditoría'
        verbose_name_plural = 'registros de auditoría'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['empresa', 'timestamp']),
            models.Index(fields=['trace_id']),
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['origin', 'timestamp']),
        ]

    def __str__(self):
        user_str = str(self.user) if self.user else '—'
        return (
            f'{user_str} — {self.get_action_display()} — '
            f'{self.model_name} — {self.timestamp:%d/%m/%Y %H:%M}'
        )

    def save(self, *args, **kwargs):
        if self.pk:
            raise TypeError('AuditLog es append-only. No se permiten actualizaciones.')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError('AuditLog es append-only. No se permiten eliminaciones.')

    @property
    def has_changes(self):
        return bool(self.changes)

    @property
    def changed_fields(self):
        return list(self.changes.keys()) if self.changes else []


class RetentionPolicy(models.Model):
    """
    Política general de conservación documental.
    Configurable por categoría según normativa.
    """

    class Category(models.TextChoices):
        AUDIT_LOG = 'audit_log', 'Registros de auditoría'
        ACCIDENTS = 'accidents', 'Accidentes e incidentes'
        PREVENTION_DOCS = 'prevention_docs', 'Documentación preventiva'
        HEALTH_SURVEILLANCE = 'health_surveillance', 'Vigilancia de la salud'
        TRAINING = 'training', 'Formación'
        TECHNICAL_LOGS = 'technical_logs', 'Logs técnicos'
        BACKUPS = 'backups', 'Copias de seguridad'
        LEGAL_DOCS = 'legal_docs', 'Documentación legal'

    category = models.CharField(
        'categoría',
        max_length=30,
        choices=Category.choices,
        unique=True,
    )
    retention_days = models.PositiveIntegerField(
        'días de retención',
        help_text='0 = retención indefinida.',
    )
    description = models.TextField(
        'descripción',
        blank=True,
        default='',
    )
    legal_reference = models.CharField(
        'referencia legal',
        max_length=300,
        blank=True,
        default='',
    )
    anonymize = models.BooleanField(
        'anonimizar en vez de eliminar',
        default=True,
        help_text='Si es True, se anonimizan los datos en vez de borrarlos.',
    )
    is_active = models.BooleanField('activa', default=True)

    created_at = models.DateTimeField('creado el', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado el', auto_now=True)

    class Meta:
        verbose_name = 'política de conservación'
        verbose_name_plural = 'políticas de conservación'
        ordering = ['category']

    def __str__(self):
        return (
            f'{self.get_category_display()} — '
            f'{self.retention_days} días'
        )
