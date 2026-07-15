import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.core.mixins import AuditFieldsMixin


def document_upload_path(instance, filename):
    company_id = instance.company_id or 'sin_empresa'
    return f'documents/company_{company_id}/{instance.category.slug}/{filename}'


class DocumentCategory(AuditFieldsMixin, models.Model):
    class Scope(models.TextChoices):
        GENERAL = 'general', 'General'
        COMPANY = 'company', 'Empresa'
        WORKCENTER = 'workcenter', 'Centro de trabajo'
        WORKER = 'worker', 'Trabajador'
        JOB_POSITION = 'job_position', 'Puesto de trabajo'

    name = models.CharField('nombre', max_length=150, unique=True)
    slug = models.SlugField('slug', max_length=160, unique=True)
    scope = models.CharField(
        'ámbito',
        max_length=30,
        choices=Scope.choices,
        default=Scope.GENERAL
    )
    description = models.TextField('descripción', blank=True)
    is_mandatory = models.BooleanField('obligatorio', default=False)
    default_validity_days = models.PositiveIntegerField(
        'validez por defecto (días)',
        null=True,
        blank=True
    )
    is_active = models.BooleanField('activo', default=True)

    created_at = models.DateTimeField('creado el', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado el', auto_now=True)

    class Meta:
        verbose_name = 'categoría documental'
        verbose_name_plural = 'categorías documentales'
        ordering = ['name']

    def __str__(self):
        return self.name


class Document(AuditFieldsMixin, models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Borrador'
        VALID = 'valid', 'Vigente'
        EXPIRED = 'expired', 'Caducado'
        REVOKED = 'revoked', 'Revocado'
        ARCHIVED = 'archived', 'Archivado'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='empresa'
    )
    category = models.ForeignKey(
        'documents.DocumentCategory',
        on_delete=models.PROTECT,
        related_name='documents',
        verbose_name='categoría'
    )

    title = models.CharField('título', max_length=255)
    description = models.TextField('descripción', blank=True)
    file = models.FileField('archivo', upload_to=document_upload_path)

    version = models.CharField('versión', max_length=50, default='1.0')
    code = models.CharField('código documental', max_length=100, blank=True)

    issue_date = models.DateField('fecha de emisión', null=True, blank=True)
    review_date = models.DateField('fecha de revisión', null=True, blank=True)
    expiry_date = models.DateField('fecha de caducidad', null=True, blank=True)

    status = models.CharField(
        'estado',
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    is_confidential = models.BooleanField('confidencial', default=False)

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_documents',
        verbose_name='subido por'
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='tipo de objeto'
    )
    object_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name='id del objeto'
    )
    content_object = GenericForeignKey('content_type', 'object_id')

    notes = models.TextField('observaciones', blank=True)

    created_at = models.DateTimeField('creado el', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado el', auto_now=True)

    class Meta:
        verbose_name = 'documento'
        verbose_name_plural = 'documentos'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
