from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from apps.core.mixins import AuditFieldsMixin


def company_logo_upload_path(instance, filename):
    company_identifier = instance.pk or 'tmp'
    return f'companies/logos/{company_identifier}/{filename}'


class Company(AuditFieldsMixin, models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Activa'
        INACTIVE = 'inactive', 'Inactiva'
        PROSPECT = 'prospect', 'Prospecto'

    legal_name = models.CharField('razón social', max_length=255)
    trade_name = models.CharField('nombre comercial', max_length=255, blank=True)
    tax_id = models.CharField('CIF/NIF', max_length=20, unique=True)
    email = models.EmailField('correo electrónico', blank=True)
    phone = models.CharField('teléfono', max_length=20, blank=True)
    website = models.URLField('sitio web', blank=True)

    address = models.CharField('dirección', max_length=255, blank=True)
    postal_code = models.CharField('código postal', max_length=12, blank=True)
    city = models.CharField('ciudad', max_length=100, blank=True)
    province = models.CharField('provincia', max_length=100, blank=True)
    autonomous_community = models.CharField('comunidad autónoma', max_length=100, blank=True)
    country = models.CharField('país', max_length=100, default='España')

    activity = models.CharField('actividad', max_length=255, blank=True)
    cnae = models.CharField('CNAE', max_length=10, blank=True)
    workforce_size = models.PositiveIntegerField('número de trabajadores', null=True, blank=True)

    logo = models.ImageField(
        'logo',
        upload_to=company_logo_upload_path,
        blank=True,
        null=True
    )

    status = models.CharField(
        'estado',
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    notes = models.TextField('observaciones', blank=True)

    created_at = models.DateTimeField('creado el', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado el', auto_now=True)

    class Meta:
        verbose_name = 'empresa'
        verbose_name_plural = 'empresas'
        ordering = ['legal_name']

    def __str__(self):
        return self.trade_name or self.legal_name


class CompanyMembership(AuditFieldsMixin, models.Model):
    class Role(models.TextChoices):
        COMPANY_ADMIN = 'company_admin', 'Administrador empresa'
        TECHNICIAN = 'technician', 'Técnico PRL'
        MANAGER = 'manager', 'Responsable'
        READER = 'reader', 'Solo lectura'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='company_memberships',
        verbose_name='usuario'
    )
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name='empresa'
    )
    role = models.CharField(
        'rol',
        max_length=30,
        choices=Role.choices,
        default=Role.READER
    )
    is_active = models.BooleanField('activo', default=True)
    is_default = models.BooleanField('empresa por defecto', default=False)

    created_at = models.DateTimeField('creado el', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado el', auto_now=True)

    class Meta:
        verbose_name = 'membresía de empresa'
        verbose_name_plural = 'membresías de empresa'
        ordering = ['company__legal_name']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'company'],
                name='unique_user_company_membership'
            ),
            models.UniqueConstraint(
                fields=['user'],
                condition=Q(is_default=True, is_active=True),
                name='unique_active_default_company_per_user'
            ),
        ]

    def clean(self):
        errors = {}

        if self.is_default and not self.is_active:
            errors['is_default'] = 'Una empresa por defecto debe estar activa.'

        if self.user_id and self.company_id:
            qs = CompanyMembership.objects.filter(
                user=self.user,
                company=self.company
            )
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                errors['company'] = 'Este usuario ya tiene una membresía para esta empresa.'

        if self.is_default and self.is_active and self.user_id:
            qs = CompanyMembership.objects.filter(
                user=self.user,
                is_default=True,
                is_active=True
            )
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                errors['is_default'] = 'Este usuario ya tiene otra empresa por defecto activa.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user} - {self.company} ({self.get_role_display()})'