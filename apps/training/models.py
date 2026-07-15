from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from datetime import timedelta
from django.utils import timezone

from apps.core.mixins import AuditFieldsMixin

class TrainingCategory(AuditFieldsMixin, models.Model):
    name = models.CharField('nombre', max_length=150, unique=True)
    code = models.CharField('código', max_length=50, unique=True, blank=True)
    description = models.TextField('descripción', blank=True)
    is_active = models.BooleanField('activa', default=True)

    created_at = models.DateTimeField('creado el', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado el', auto_now=True)

    class Meta:
        verbose_name = 'categoría de formación'
        verbose_name_plural = 'categorías de formación'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name


class TrainingCourse(AuditFieldsMixin, models.Model):
    class Modality(models.TextChoices):
        PRESENTIAL = 'presential', 'Presencial'
        ONLINE = 'online', 'Online'
        MIXED = 'mixed', 'Mixta'

    class ValidityUnit(models.TextChoices):
        DAYS = 'days', 'Días'
        MONTHS = 'months', 'Meses'
        YEARS = 'years', 'Años'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Activo'
        INACTIVE = 'inactive', 'Inactivo'

    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='training_courses',
        verbose_name='empresa',
        null=True,
        blank=True,
        help_text='Déjalo vacío si el curso es una plantilla general reutilizable.'
    )
    category = models.ForeignKey(
        'training.TrainingCategory',
        on_delete=models.PROTECT,
        related_name='courses',
        verbose_name='categoría'
    )
    required_for_job_positions = models.ManyToManyField(
        'workers.JobPosition',
        related_name='required_training_courses',
        verbose_name='obligatoria para puestos',
        blank=True
    )

    name = models.CharField('nombre', max_length=200)
    code = models.CharField('código', max_length=50, blank=True)
    description = models.TextField('descripción', blank=True)
    objective = models.TextField('objetivo', blank=True)
    content = models.TextField('contenido', blank=True)

    modality = models.CharField(
        'modalidad',
        max_length=20,
        choices=Modality.choices,
        default=Modality.PRESENTIAL
    )

    duration_hours = models.DecimalField(
        'duración (horas)',
        max_digits=6,
        decimal_places=2,
        default=0
    )

    is_mandatory = models.BooleanField('obligatoria', default=True)
    requires_renewal = models.BooleanField('requiere renovación', default=False)
    validity_value = models.PositiveIntegerField('validez', null=True, blank=True)
    validity_unit = models.CharField(
        'unidad de validez',
        max_length=10,
        choices=ValidityUnit.choices,
        blank=True
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
        verbose_name = 'curso de formación'
        verbose_name_plural = 'cursos de formación'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'name'],
                name='unique_training_course_company_name'
            ),
            models.UniqueConstraint(
                fields=['company', 'code'],
                name='unique_training_course_company_code'
            ),
        ]
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['code']),
            models.Index(fields=['status']),
            models.Index(fields=['is_mandatory']),
            models.Index(fields=['requires_renewal']),
        ]

    def clean(self):
        if self.requires_renewal:
            if not self.validity_value or not self.validity_unit:
                raise ValidationError({
                    'validity_value': 'Debes indicar la validez si el curso requiere renovación.',
                    'validity_unit': 'Debes indicar la unidad de validez si el curso requiere renovación.',
                })

        if not self.requires_renewal:
            self.validity_value = None
            self.validity_unit = ''

    def __str__(self):
        if self.company:
            return f'{self.company} - {self.name}'
        return self.name


class TrainingRecord(AuditFieldsMixin, models.Model):
    class Status(models.TextChoices):
        PLANNED = 'planned', 'Planificada'
        IN_PROGRESS = 'in_progress', 'En curso'
        COMPLETED = 'completed', 'Completada'
        EXPIRED = 'expired', 'Caducada'
        CANCELLED = 'cancelled', 'Cancelada'

    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='training_records',
        verbose_name='empresa',
        null=True,
        blank=True
    )
    worker = models.ForeignKey(
        'workers.Worker',
        on_delete=models.CASCADE,
        related_name='training_records',
        verbose_name='trabajador'
    )
    job_position = models.ForeignKey(
        'workers.JobPosition',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='training_records',
        verbose_name='puesto de trabajo'
    )
    course = models.ForeignKey(
        'training.TrainingCourse',
        on_delete=models.PROTECT,
        related_name='records',
        verbose_name='curso'
    )

    status = models.CharField(
        'estado',
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED
    )

    planned_date = models.DateField('fecha planificada', null=True, blank=True)
    completed_date = models.DateField('fecha de realización', null=True, blank=True)
    expiry_date = models.DateField('fecha de caducidad', null=True, blank=True)

    trainer_name = models.CharField('formador', max_length=150, blank=True)
    training_entity = models.CharField('entidad formadora', max_length=150, blank=True)
    certificate_number = models.CharField('nº de certificado', max_length=100, blank=True)

    attendance_percentage = models.PositiveSmallIntegerField(
        'asistencia (%)',
        null=True,
        blank=True
    )
    score = models.DecimalField(
        'calificación',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    notes = models.TextField('observaciones', blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_training_records',
        verbose_name='creado por'
    )
    created_at = models.DateTimeField('creado el', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado el', auto_now=True)
    effectiveness_validated = models.BooleanField(default=False)
    effectiveness_notes = models.TextField(blank=True)
    evidence_document = models.ForeignKey(
        'documents.Document',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='training_records'
    )
    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_training_records'
    )
    validated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'registro de formación'
        verbose_name_plural = 'registros de formación'
        ordering = ['-planned_date', '-completed_date', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['worker', 'course', 'completed_date'],
                name='unique_worker_course_completed_date'
            )
        ]
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['worker']),
            models.Index(fields=['course']),
            models.Index(fields=['status']),
            models.Index(fields=['planned_date']),
            models.Index(fields=['completed_date']),
            models.Index(fields=['expiry_date']),
        ]

    def clean(self):
        if self.worker and self.company and self.worker.company_id != self.company_id:
            raise ValidationError({
                'company': 'La empresa del registro debe coincidir con la empresa del trabajador.'
            })

        if self.job_position and self.worker and self.job_position_id != self.worker.job_position_id:
            raise ValidationError({
                'job_position': 'El puesto del registro debe coincidir con el puesto actual del trabajador.'
            })

        if self.course and self.company and self.course.company_id:
            if self.course.company_id != self.company_id:
                raise ValidationError({
                    'course': 'El curso pertenece a otra empresa.'
                })

        if self.status == self.Status.COMPLETED and not self.completed_date:
            raise ValidationError({
                'completed_date': 'Debes indicar la fecha de realización si la formación está completada.'
            })

        if self.expiry_date and self.completed_date and self.expiry_date < self.completed_date:
            raise ValidationError({
                'expiry_date': 'La fecha de caducidad no puede ser anterior a la fecha de realización.'
            })

    @property
    def expiry_status(self):
        if not self.expiry_date:
            return 'no_expiry'

        today = timezone.localdate()

        if self.expiry_date < today:
            return 'expired'

        if self.expiry_date <= today + timedelta(days=30):
            return 'expiring'

        return 'valid'


    @property
    def expiry_status_label(self):
        return {
            'no_expiry': 'Sin caducidad',
            'expired': 'Caducado',
            'expiring': 'Caduca pronto',
            'valid': 'Vigente',
        }.get(self.expiry_status, 'Sin estado')


    @property
    def expiry_badge_class(self):
        return {
            'no_expiry': 'badge-neutral',
            'expired': 'badge-danger',
            'expiring': 'badge-warning',
            'valid': 'badge-success',
        }.get(self.expiry_status, 'badge-neutral')


    @property
    def expiry_days_delta(self):
        if not self.expiry_date:
            return None
        return (self.expiry_date - timezone.localdate()).days


    @property
    def expiry_help_text(self):
        delta = self.expiry_days_delta

        if delta is None:
            return 'No aplica vigencia'

        if delta < 0:
            days = abs(delta)
            return f'Vencido hace {days} día{"s" if days != 1 else ""}'

        if delta == 0:
            return 'Caduca hoy'

        if delta <= 30:
            return f'Caduca en {delta} día{"s" if delta != 1 else ""}'

        return f'Vigente · {delta} días restantes'
    def save(self, *args, **kwargs):
        if self.worker and not self.company_id:
            self.company = self.worker.company

        if self.worker and not self.job_position_id:
            self.job_position = self.worker.job_position

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.worker} - {self.course}'


class TrainingDocument(AuditFieldsMixin, models.Model):
    record = models.ForeignKey(
        'training.TrainingRecord',
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='registro de formación'
    )
    name = models.CharField('nombre', max_length=200)
    file = models.FileField('archivo', upload_to='training/documents/')
    document_type = models.CharField('tipo de documento', max_length=100, blank=True)
    notes = models.TextField('observaciones', blank=True)
    uploaded_at = models.DateTimeField('subido el', auto_now_add=True)

    class Meta:
        verbose_name = 'documento de formación'
        verbose_name_plural = 'documentos de formación'
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.name


class TrainingRequirement(AuditFieldsMixin, models.Model):
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='training_requirements'
    )
    job_position = models.ForeignKey(
        'workers.JobPosition',
        on_delete=models.CASCADE,
        related_name='training_requirements'
    )
    course = models.ForeignKey(
        'training.TrainingCourse',
        on_delete=models.CASCADE,
        related_name='requirements'
    )
    is_mandatory = models.BooleanField(default=True)
    renewal_months = models.PositiveIntegerField(blank=True, null=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Requisito formativo'
        verbose_name_plural = 'Requisitos formativos'
        unique_together = ('company', 'job_position', 'course')
        ordering = ['job_position__name', 'course__name']

    def __str__(self):
        return f'{self.job_position} · {self.course}'


class TrainingNeed(AuditFieldsMixin, models.Model):
    STATUS_PENDING = 'pending'
    STATUS_SCHEDULED = 'scheduled'
    STATUS_COMPLETED = 'completed'
    STATUS_EXEMPT = 'exempt'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendiente'),
        (STATUS_SCHEDULED, 'Planificada'),
        (STATUS_COMPLETED, 'Completada'),
        (STATUS_EXEMPT, 'Exenta'),
    ]

    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='training_needs'
    )
    worker = models.ForeignKey(
        'workers.Worker',
        on_delete=models.CASCADE,
        related_name='training_needs'
    )
    job_position = models.ForeignKey(
        'workers.JobPosition',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='training_needs'
    )
    requirement = models.ForeignKey(
        'training.TrainingRequirement',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='training_needs'
    )
    course = models.ForeignKey(
        'training.TrainingCourse',
        on_delete=models.CASCADE,
        related_name='training_needs'
    )
    due_date = models.DateField(blank=True, null=True)
    priority = models.PositiveSmallIntegerField(default=2)  # 1 alta, 2 media, 3 baja
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    source = models.CharField(
        max_length=30,
        default='job_position',
        help_text='Origen de la necesidad: puesto, cambio, incidencia, auditoría, etc.'
    )
    notes = models.TextField(blank=True)

    related_record = models.ForeignKey(
        'training.TrainingRecord',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_needs'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Necesidad formativa'
        verbose_name_plural = 'Necesidades formativas'
        ordering = ['priority', 'due_date', 'worker__last_name']

    def __str__(self):
        return f'{self.worker} · {self.course}'

    @property
    def priority_label(self):
        return {1: 'Alta', 2: 'Media', 3: 'Baja'}.get(self.priority, 'Media')

    @property
    def priority_badge_class(self):
        return {1: 'badge-danger', 2: 'badge-warning', 3: 'badge-info'}.get(self.priority, 'badge-neutral')


class TrainingAlert(AuditFieldsMixin, models.Model):
    TYPE_EXPIRING = 'expiring'
    TYPE_EXPIRED = 'expired'
    TYPE_MISSING = 'missing'
    TYPE_EFFECTIVENESS = 'effectiveness'

    TYPE_CHOICES = [
        (TYPE_EXPIRING, 'Caducidad próxima'),
        (TYPE_EXPIRED, 'Caducado'),
        (TYPE_MISSING, 'Formación pendiente'),
        (TYPE_EFFECTIVENESS, 'Eficacia pendiente'),
    ]

    STATUS_OPEN = 'open'
    STATUS_CLOSED = 'closed'

    STATUS_CHOICES = [
        (STATUS_OPEN, 'Abierta'),
        (STATUS_CLOSED, 'Cerrada'),
    ]

    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='training_alerts'
    )
    worker = models.ForeignKey(
        'workers.Worker',
        on_delete=models.CASCADE,
        related_name='training_alerts',
        null=True,
        blank=True
    )
    
    course = models.ForeignKey(
        'training.TrainingCourse',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alerts'
    )
    record = models.ForeignKey(
        'training.TrainingRecord',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alerts'
    )
    need = models.ForeignKey(
        'training.TrainingNeed',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alerts'
    )

    alert_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    due_date = models.DateField(blank=True, null=True)
    triggered_on = models.DateField(default=timezone.localdate)

    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Alerta de formación'
        verbose_name_plural = 'Alertas de formación'
        ordering = ['status', 'due_date', '-created_at']

    def __str__(self):
        return self.title