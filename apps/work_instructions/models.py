from django.db import models
from django.conf import settings
from apps.companies.models import Company
from apps.workers.models import JobPosition
from apps.core.mixins import AuditFieldsMixin


class InstruccionTrabajo(AuditFieldsMixin, models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='instrucciones_trabajo')
    titulo = models.CharField(max_length=200)
    codigo = models.CharField(max_length=50, blank=True, default='')
    puesto_trabajo = models.ForeignKey(JobPosition, on_delete=models.SET_NULL, null=True, blank=True, related_name='instrucciones')
    contenido = models.TextField(blank=True, default='')
    file = models.FileField(upload_to='instrucciones_trabajo/', blank=True)
    revision = models.PositiveIntegerField(default=1)
    fecha = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['titulo']
        verbose_name = 'Instrucción de Trabajo'
        verbose_name_plural = 'Instrucciones de Trabajo'
        unique_together = ['company', 'codigo']

    def __str__(self):
        return f"{self.codigo} — {self.titulo}" if self.codigo else self.titulo
