from django.db import models
from django.conf import settings
from apps.companies.models import Company
from apps.workers.models import Worker
from apps.core.mixins import AuditFieldsMixin


class ReconocimientoMedico(AuditFieldsMixin, models.Model):
    TIPO_CHOICES = [
        ('inicial', 'Reconocimiento Inicial'),
        ('periodico', 'Reconocimiento Periódico'),
        ('especial', 'Reconocimiento Especial'),
        ('aptitud', 'Control de Aptitud'),
    ]
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='reconocimientos_medicos')
    trabajador = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='reconocimientos_medicos')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    fecha = models.DateField()
    proximo_reconocimiento = models.DateField(null=True, blank=True)
    apto = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True, default='')
    medico = models.CharField(max_length=200, blank=True, default='')
    file = models.FileField(upload_to='reconocimientos_medicos/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Reconocimiento Médico'
        verbose_name_plural = 'Reconocimientos Médicos'

    def __str__(self):
        return f"{self.trabajador} — {self.get_tipo_display()} ({self.fecha})"

    @property
    def badge_color(self):
        return 'success' if self.apto else 'danger'


class ControlSalud(AuditFieldsMixin, models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='controles_salud')
    trabajador = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='controles_salud')
    fecha = models.DateField()
    tipo_control = models.CharField(max_length=200)
    resultados = models.TextField(blank=True, default='')
    recomendaciones = models.TextField(blank=True, default='')
    file = models.FileField(upload_to='controles_salud/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Control de Salud'
        verbose_name_plural = 'Controles de Salud'

    def __str__(self):
        return f"{self.trabajador} — {self.tipo_control} ({self.fecha})"
