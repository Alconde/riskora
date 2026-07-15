from django.conf import settings
from django.db import models
from django.utils import timezone


class RequisitoAutorizacion(models.Model):
    """
    Catálogo de requisitos de autorización: equipos o trabajos que
    requieren capacitación/certificación específica del trabajador.
    company=NULL → catálogo global del sistema.
    """

    class Tipo(models.TextChoices):
        EQUIPO = 'equipo', 'Equipo de trabajo'
        TRABAJO = 'trabajo', 'Trabajo o actividad'

    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='requisitos_autorizacion',
        verbose_name='empresa',
        help_text='Vacío = catálogo global del sistema',
    )
    nombre = models.CharField('nombre del requisito', max_length=300)
    tipo = models.CharField('tipo', max_length=20, choices=Tipo.choices)
    categoria = models.CharField(
        'categoría',
        max_length=100,
        blank=True,
        default='',
        help_text='Agrupación libre: Maquinaria, Trabajos especiales, etc.',
    )
    normativa = models.CharField(
        'referencia normativa',
        max_length=300,
        blank=True,
        default='',
        help_text='Ej: RD 1215/1997, RD 2177/2004',
    )
    descripcion = models.TextField('descripción', blank=True, default='')
    activo = models.BooleanField('activo', default=True)

    created_at = models.DateTimeField('creado el', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado el', auto_now=True)

    class Meta:
        verbose_name = 'requisito de autorización'
        verbose_name_plural = 'requisitos de autorización'
        ordering = ['tipo', 'categoria', 'nombre']
        indexes = [
            models.Index(fields=['empresa', 'activo']),
            models.Index(fields=['tipo', 'activo']),
        ]

    def __str__(self):
        return f'{self.nombre} ({self.get_tipo_display()})'

    @property
    def es_global(self):
        return self.empresa_id is None

    @property
    def total_autorizados(self):
        hoy = timezone.now().date()
        return self.autorizaciones.filter(
            activa=True,
            fecha_autorizacion__lte=hoy,
        ).filter(
            models.Q(fecha_caducidad__isnull=True) | models.Q(fecha_caducidad__gte=hoy),
        ).count()

    @property
    def autorizaciones_proximas_caducar(self):
        from datetime import timedelta
        hoy = timezone.now().date()
        limite = hoy + timedelta(days=30)
        return self.autorizaciones.filter(
            activa=True,
            fecha_caducidad__gte=hoy,
            fecha_caducidad__lte=limite,
        ).count()

    @property
    def autorizaciones_caducadas(self):
        hoy = timezone.now().date()
        return self.autorizaciones.filter(
            activa=True,
            fecha_caducidad__lt=hoy,
        ).count()

    def trabajadores_sin_autorizacion(self, empresa):
        from apps.workers.models import Worker
        autorizados_ids = self.autorizaciones.filter(
            activa=True,
        ).values_list('trabajador_id', flat=True)
        return Worker.objects.filter(
            company=empresa,
            employment_status='active',
        ).exclude(id__in=autorizados_ids)


class AutorizacionTrabajador(models.Model):
    """
    Registro de autorización de un trabajador para un requisito específico.
    """

    class Estado(models.TextChoices):
        ACTIVA = 'activa', 'Activa'
        CADUCADA = 'caducada', 'Caducada'
        SUSPENDIDA = 'suspendida', 'Suspendida'
        PENDIENTE = 'pendiente', 'Pendiente de renovación'

    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='autorizaciones_trabajadores',
        verbose_name='empresa',
    )
    trabajador = models.ForeignKey(
        'workers.Worker',
        on_delete=models.CASCADE,
        related_name='autorizaciones',
        verbose_name='trabajador',
    )
    requisito = models.ForeignKey(
        RequisitoAutorizacion,
        on_delete=models.CASCADE,
        related_name='autorizaciones',
        verbose_name='requisito',
    )
    fecha_autorizacion = models.DateField('fecha de autorización')
    fecha_caducidad = models.DateField(
        'fecha de caducidad',
        null=True,
        blank=True,
        help_text='Dejar vacío si no caduca',
    )
    entidad_emisora = models.CharField(
        'entidad emisora',
        max_length=200,
        blank=True,
        default='',
        help_text='Ej: INSST, AENOR, empresa formativa',
    )
    numero_certificado = models.CharField(
        'número de certificado',
        max_length=100,
        blank=True,
        default='',
    )
    archivo = models.FileField(
        'certificado / acreditación',
        upload_to='autorizaciones/',
        blank=True,
    )
    observaciones = models.TextField('observaciones', blank=True, default='')
    activa = models.BooleanField('autorización activa', default=True)

    created_at = models.DateTimeField('creado el', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado el', auto_now=True)

    class Meta:
        verbose_name = 'autorización de trabajador'
        verbose_name_plural = 'autorizaciones de trabajadores'
        ordering = ['requisito', 'trabajador']
        indexes = [
            models.Index(fields=['empresa', 'activa']),
            models.Index(fields=['trabajador', 'activa']),
            models.Index(fields=['fecha_caducidad']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['trabajador', 'requisito', 'fecha_autorizacion'],
                name='uniq_autorizacion_trab_req_fecha',
            ),
        ]

    def __str__(self):
        return f'{self.trabajador} - {self.requisito}'

    @property
    def estado(self):
        if not self.activa:
            return self.Estado.SUSPENDIDA
        if self.fecha_caducidad:
            hoy = timezone.now().date()
            if self.fecha_caducidad < hoy:
                return self.Estado.CADUCADA
            from datetime import timedelta
            if self.fecha_caducidad <= hoy + timedelta(days=30):
                return self.Estado.PENDIENTE
        return self.Estado.ACTIVA

    @property
    def badge_estado(self):
        return {
            self.Estado.ACTIVA: 'badge-success',
            self.Estado.CADUCADA: 'badge-danger',
            self.Estado.SUSPENDIDA: 'badge-secondary',
            self.Estado.PENDIENTE: 'badge-warning',
        }.get(self.estado, 'badge-secondary')

    @property
    def esta_valida(self):
        return self.estado == self.Estado.ACTIVA

    @property
    def dias_para_caducidad(self):
        if not self.fecha_caducidad:
            return None
        delta = self.fecha_caducidad - timezone.now().date()
        return delta.days
