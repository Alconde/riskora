from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

from apps.core.mixins import AuditFieldsMixin


class JobPosition(AuditFieldsMixin, models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Activo'
        INACTIVE = 'inactive', 'Inactivo'

    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='job_positions',
        verbose_name='empresa'
    )
    name = models.CharField('nombre del puesto', max_length=150)
    department = models.CharField('departamento', max_length=150, blank=True)
    description = models.TextField('descripción', blank=True)
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
        verbose_name = 'puesto de trabajo'
        verbose_name_plural = 'puestos de trabajo'
        ordering = ['company__legal_name', 'name']
        unique_together = ('company', 'name')

    def __str__(self):
        return f'{self.company} - {self.name}'
    
class Worker(AuditFieldsMixin, models.Model):
    class EmploymentStatus(models.TextChoices):
        ACTIVE = 'active', 'Activo'
        LEAVE = 'leave', 'Baja'
        INACTIVE = 'inactive', 'Inactivo'

    phone_validator = RegexValidator(
        regex=r'^[0-9+\s()-]{7,20}$',
        message='Introduce un teléfono válido.'
    )

    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='workers',
        verbose_name='empresa'
    )
    work_center = models.ForeignKey(
        'workcenters.WorkCenter',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='workers',
        verbose_name='centro de trabajo'
    )
    job_position = models.ForeignKey(
        'workers.JobPosition',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='workers',
        verbose_name='puesto de trabajo'
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='worker_profile',
        verbose_name='usuario del sistema'
    )

    first_name = models.CharField('nombre', max_length=100)
    last_name = models.CharField('apellidos', max_length=150)
    national_id = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='DNI / NIE',
        unique=True,  # o True si luego quieres unicidad, pero con null=True
    )
    email = models.EmailField('correo electrónico', blank=True)
    phone = models.CharField(
        'teléfono',
        max_length=20,
        blank=True,
        validators=[phone_validator]
    )

    employee_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='código de empleado'
    )
    social_security_number = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name='Nº Seguridad Social',
        unique=True,
    )

    hire_date = models.DateField('fecha de alta', null=True, blank=True)
    birth_date = models.DateField('fecha de nacimiento', null=True, blank=True)

    employment_status = models.CharField(
        'estado laboral',
        max_length=20,
        choices=EmploymentStatus.choices,
        default=EmploymentStatus.ACTIVE
    )

    especially_sensitive = models.BooleanField('especial sensibilidad', default=False)
    temporary_worker = models.BooleanField('trabajador temporal', default=False)

    notes = models.TextField('observaciones', blank=True)

    created_at = models.DateTimeField('creado el', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado el', auto_now=True)

    class Meta:
        verbose_name = 'trabajador'
        verbose_name_plural = 'trabajadores'
        ordering = ['company__legal_name', 'last_name', 'first_name']
        unique_together = ('company', 'employee_code')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'.strip()
