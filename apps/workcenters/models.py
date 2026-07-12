from django.db import models


class WorkCenter(models.Model):
    class RiskLevel(models.TextChoices):
        LOW = 'low', 'Bajo'
        MEDIUM = 'medium', 'Medio'
        HIGH = 'high', 'Alto'
        VERY_HIGH = 'very_high', 'Muy alto'

    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='work_centers',
        verbose_name='empresa'
    )

    name = models.CharField('nombre del centro', max_length=255)
    code = models.CharField('código interno', max_length=50, blank=True)
    address = models.CharField('dirección', max_length=255)
    postal_code = models.CharField('código postal', max_length=12, blank=True)
    city = models.CharField('ciudad', max_length=100, blank=True)
    province = models.CharField('provincia', max_length=100, blank=True)

    contact_person = models.CharField('persona de contacto', max_length=255, blank=True)
    contact_phone = models.CharField('teléfono de contacto', max_length=20, blank=True)
    contact_email = models.EmailField('correo de contacto', blank=True)

    activity = models.CharField('actividad del centro', max_length=255, blank=True)
    worker_count = models.PositiveIntegerField('número de trabajadores', null=True, blank=True)
    risk_level = models.CharField(
        'nivel de riesgo',
        max_length=20,
        choices=RiskLevel.choices,
        default=RiskLevel.LOW
    )

    is_active = models.BooleanField('activo', default=True)
    notes = models.TextField('observaciones', blank=True)

    created_at = models.DateTimeField('creado el', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado el', auto_now=True)

    class Meta:
        verbose_name = 'centro de trabajo'
        verbose_name_plural = 'centros de trabajo'
        ordering = ['company__legal_name', 'name']
        unique_together = ('company', 'name')

    def __str__(self):
        return f'{self.company} - {self.name}'
