from django.db import models
from django.conf import settings
from apps.companies.models import Company


class MedidaEmergencia(models.Model):
    TIPO_CHOICES = [
        ('plan', 'Plan de Emergencia'),
        ('extintor', 'Extintor'),
        ('evacuacion', 'Ruta de Evacuación'),
        ('simulacro', 'Simulacro'),
        ('protocolo', 'Protocolo de Actuación'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='medidas_emergencia')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, default='')
    ubicacion = models.CharField(max_length=200, blank=True, default='')
    fecha = models.DateField(null=True, blank=True)
    proximo_simulacro = models.DateField(null=True, blank=True)
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='medidas_emergencia'
    )
    file = models.FileField(upload_to='medidas_emergencia/', blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['tipo', 'titulo']
        verbose_name = 'Medida de Emergencia'
        verbose_name_plural = 'Medidas de Emergencia'

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.titulo}"

    @property
    def badge_color(self):
        return {
            'plan': 'info',
            'extintor': 'success',
            'evacuacion': 'warning',
            'simulacro': 'accent',
            'protocolo': 'secondary',
        }.get(self.tipo, 'secondary')

    @property
    def icon_svg(self):
        icons = {
            'plan': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14,2 14,8 20,8"/></svg>',
            'extintor': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 2a5 5 0 0 1 5 5v2a5 5 0 0 1-10 0V7a5 5 0 0 1 5-5Z"/><path d="M12 12v6"/><path d="M8 18h8"/></svg>',
            'evacuacion': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="5" r="3"/><path d="M12 8v4l3 5"/><path d="M12 12l-3 5"/></svg>',
            'simulacro': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12"/><path d="M12 6v6l4 2"/></svg>',
            'protocolo': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M9 12h6"/><path d="M9 16h6"/><path d="M17 2H7a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2Z"/></svg>',
        }
        return icons.get(self.tipo, '')


class HistorialSimulacro(models.Model):
    medida = models.ForeignKey(MedidaEmergencia, on_delete=models.CASCADE, related_name='historial')
    fecha = models.DateField()
    participantes = models.PositiveIntegerField(default=0)
    observaciones = models.TextField(blank=True, default='')
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Historial de Simulacro'
        verbose_name_plural = 'Historial de Simulacros'

    def __str__(self):
        return f"Simulacro {self.fecha} — {self.medida.titulo}"
