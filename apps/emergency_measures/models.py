from django.db import models
from django.conf import settings
from apps.companies.models import Company
from apps.workers.models import Worker
from apps.core.mixins import AuditFieldsMixin


class MedioProteccionIncendios(AuditFieldsMixin, models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, default='')
    icono = models.CharField(max_length=50, blank=True, default='')
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Medio de Protección contra Incendios'
        verbose_name_plural = 'Medios de Protección contra Incendios'

    def __str__(self):
        return self.nombre


class EmpresaMedioProteccion(AuditFieldsMixin, models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='medios_proteccion')
    medio = models.ForeignKey(MedioProteccionIncendios, on_delete=models.CASCADE, related_name='empresas')
    cantidad = models.PositiveIntegerField(default=1)
    ubicacion = models.CharField(max_length=300, blank=True, default='')
    notas = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Medio de Protección de la Empresa'
        verbose_name_plural = 'Medios de Protección de la Empresa'
        unique_together = ['company', 'medio']

    def __str__(self):
        return f"{self.medio.nombre} ({self.cantidad})"


class PlanAutoproteccion(AuditFieldsMixin, models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='plan_autoproteccion')
    file_plan = models.FileField(upload_to='medidas_emergencia/plan/', blank=True)
    file_plano = models.FileField(upload_to='medidas_emergencia/plano/', blank=True)
    notas_plano = models.TextField(blank=True, default='')
    fecha_revision = models.DateField(null=True, blank=True)
    proxima_revision = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Plan de Autoprotección'
        verbose_name_plural = 'Planes de Autoprotección'

    def __str__(self):
        return f"Plan de Autoprotección — {self.company}"


class EquipoEmergencia(AuditFieldsMixin, models.Model):
    TIPO_CHOICES = [
        ('jefe', 'Jefe de Emergencia'),
        ('sustituto', 'Sustituto del Jefe'),
        ('intervencion', 'Equipo de Intervención'),
        ('primeros_auxilios', 'Equipo de Primeros Auxilios'),
        ('evacuacion', 'Equipo de Evacuación'),
        ('comunicaciones', 'Equipo de Comunicaciones'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='equipos_emergencia')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    nombre = models.CharField(max_length=200, blank=True, default='')
    designacion_file = models.FileField(upload_to='medidas_emergencia/designaciones/', blank=True)
    formacion_file = models.FileField(upload_to='medidas_emergencia/formacion_equipos/', blank=True)
    descripcion = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['tipo', 'nombre']
        verbose_name = 'Equipo de Emergencia'
        verbose_name_plural = 'Equipos de Emergencia'

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.nombre or self.company}"

    @property
    def badge_color(self):
        return {
            'jefe': 'danger',
            'sustituto': 'warning',
            'intervencion': 'accent',
            'primeros_auxilios': 'success',
            'evacuacion': 'info',
            'comunicaciones': 'secondary',
        }.get(self.tipo, 'secondary')


class MiembroEquipoEmergencia(AuditFieldsMixin, models.Model):
    equipo = models.ForeignKey(EquipoEmergencia, on_delete=models.CASCADE, related_name='miembros')
    trabajador = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='equipos_emergencia')
    rol = models.CharField(max_length=100, blank=True, default='')
    designacion_file = models.FileField(upload_to='medidas_emergencia/miembros_designaciones/', blank=True)
    formacion_file = models.FileField(upload_to='medidas_emergencia/miembros_formacion/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Miembro del Equipo de Emergencia'
        verbose_name_plural = 'Miembros de Equipos de Emergencia'
        unique_together = ['equipo', 'trabajador']

    def __str__(self):
        return f"{self.trabajador} — {self.equipo.get_tipo_display()}"


class RegistroSimulacro(AuditFieldsMixin, models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='simulacros')
    fecha = models.DateField()
    descripcion = models.TextField(blank=True, default='')
    participantes = models.PositiveIntegerField(default=0)
    observaciones = models.TextField(blank=True, default='')
    duracion_minutos = models.PositiveIntegerField(null=True, blank=True)
    archivo = models.FileField(upload_to='medidas_emergencia/simulacros/', blank=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Registro de Simulacro'
        verbose_name_plural = 'Registros de Simulacros'

    def __str__(self):
        return f"Simulacro {self.fecha}"


class EntregaInformacionEmergencia(AuditFieldsMixin, models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='entregas_info_emergencia')
    trabajador = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='entregas_info_emergencia')
    fecha_entrega = models.DateField()
    tipo_informacion = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, default='')
    firma_trabajador = models.BooleanField(default=False)
    archivo = models.FileField(upload_to='medidas_emergencia/entregas_info/', blank=True)
    notas = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_entrega']
        verbose_name = 'Entrega de Información de Emergencia'
        verbose_name_plural = 'Entregas de Información de Emergencia'

    def __str__(self):
        return f"{self.trabajador} — {self.tipo_informacion} ({self.fecha_entrega})"
