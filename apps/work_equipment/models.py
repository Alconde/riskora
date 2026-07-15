from django.conf import settings
from django.db import models
from django.utils import timezone
from apps.core.mixins import AuditFieldsMixin


class TipoEquipo(AuditFieldsMixin, models.Model):

    class Categoria(models.TextChoices):
        MAQUINARIA = 'maquinaria', 'Maquinaria'
        HERRAMIENTAS = 'herramientas', 'Herramientas'
        VEHICULOS = 'vehiculos', 'Vehiculos'
        ANDAMIOS = 'andamios', 'Andamios'
        GRUAS = 'gruas', 'Gruas'
        ESCALERAS = 'escaleras', 'Escaleras'
        EQUIPOS_ELEVACION = 'elevacion', 'Equipos de elevacion'
        INSTALACIONES = 'instalaciones', 'Instalaciones fijas'
        OTRO = 'otro', 'Otro'

    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='tipos_equipo',
        verbose_name='empresa',
    )
    nombre = models.CharField(max_length=200, verbose_name='nombre')
    categoria = models.CharField(
        max_length=20,
        choices=Categoria.choices,
        default=Categoria.MAQUINARIA,
        verbose_name='categoria',
    )
    descripcion = models.TextField(blank=True, verbose_name='descripcion')
    imagen = models.FileField(
        upload_to='equipos/tipos/',
        blank=True,
        verbose_name='imagen',
    )
    activo = models.BooleanField(default=True, verbose_name='activo')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'tipo de equipo'
        verbose_name_plural = 'tipos de equipo'
        ordering = ['categoria', 'nombre']

    def __str__(self):
        return f'{self.get_categoria_display()} - {self.nombre}'


class EquipoTrabajo(AuditFieldsMixin, models.Model):

    class Estado(models.TextChoices):
        OPERATIVO = 'operativo', 'Operativo'
        EN_MANTENIMIENTO = 'en_mantenimiento', 'En mantenimiento'
        RETIRADO = 'retirado', 'Retirado'
        BAJA = 'baja', 'Baja'

    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='equipos_trabajo',
        verbose_name='empresa',
    )
    tipo = models.ForeignKey(
        TipoEquipo,
        on_delete=models.CASCADE,
        related_name='equipos',
        verbose_name='tipo de equipo',
    )
    nombre = models.CharField(max_length=200, verbose_name='nombre / identificacion')
    marca = models.CharField(max_length=100, blank=True, verbose_name='marca')
    modelo = models.CharField(max_length=100, blank=True, verbose_name='modelo')
    numero_serie = models.CharField(
        max_length=100, blank=True, verbose_name='numero de serie'
    )
    numero_bien = models.CharField(
        max_length=100, blank=True, verbose_name='numero de bien'
    )
    fecha_compra = models.DateField(null=True, blank=True, verbose_name='fecha de compra')
    fecha_puesta_marcha = models.DateField(
        null=True, blank=True, verbose_name='fecha de puesta en marcha'
    )
    ubicacion = models.CharField(
        max_length=200, blank=True, verbose_name='ubicacion / centro de trabajo'
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='equipos_trabajo_responsable',
        verbose_name='responsable',
    )
    vida_util_meses = models.PositiveIntegerField(
        null=True, blank=True, verbose_name='vida util (meses)'
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.OPERATIVO,
        verbose_name='estado',
    )
    notas = models.TextField(blank=True, verbose_name='notas')
    manual_instrucciones = models.FileField(
        upload_to='equipos/manuales/',
        blank=True,
        verbose_name='manual de instrucciones (PDF)',
    )
    declaracion_ce = models.FileField(
        upload_to='equipos/declaraciones_ce/',
        blank=True,
        verbose_name='declaracion CE de conformidad (PDF)',
    )
    certificado_instalacion = models.FileField(
        upload_to='equipos/certificados_instalacion/',
        blank=True,
        verbose_name='certificado de instalacion (PDF)',
    )
    activo = models.BooleanField(default=True, verbose_name='activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'equipo de trabajo'
        verbose_name_plural = 'equipos de trabajo'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['empresa', 'estado']),
            models.Index(fields=['empresa', 'tipo']),
        ]

    def __str__(self):
        return f'{self.nombre} ({self.tipo.nombre})'

    @property
    def badge_estado(self):
        mapping = {
            'operativo': 'badge-success',
            'en_mantenimiento': 'badge-warning',
            'retirado': 'badge-secondary',
            'baja': 'badge-danger',
        }
        return mapping.get(self.estado, 'badge-secondary')

    @property
    def total_revisiones(self):
        return self.revisiones.count()

    @property
    def ultima_revision(self):
        return self.revisiones.order_by('-fecha').first()

    @property
    def proxima_revision_fecha(self):
        ultima = self.ultima_revision
        if ultima and ultima.proxima_revision:
            return ultima.proxima_revision
        return None

    @property
    def revision_pendiente(self):
        proxima = self.proxima_revision_fecha
        if not proxima:
            return False
        return proxima <= timezone.localdate()

    @property
    def total_mantenimientos(self):
        return self.mantenimientos.count()

    @property
    def document_count(self):
        docs = [
            self.manual_instrucciones,
            self.declaracion_ce,
            self.certificado_instalacion,
        ]
        return sum(1 for d in docs if d)


class RevisionEquipo(AuditFieldsMixin, models.Model):

    class Resultado(models.TextChoices):
        CONFORME = 'conforme', 'Conforme'
        OBSERVACIONES = 'observaciones', 'Con observaciones'
        NO_CONFORME = 'no_conforme', 'No conforme'
        REPARADO = 'reparado', 'Reparado necesario'

    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='revisiones_equipo',
        verbose_name='empresa',
    )
    equipo = models.ForeignKey(
        EquipoTrabajo,
        on_delete=models.CASCADE,
        related_name='revisiones',
        verbose_name='equipo',
    )
    fecha = models.DateField(verbose_name='fecha de revision')
    resultado = models.CharField(
        max_length=20,
        choices=Resultado.choices,
        default=Resultado.CONFORME,
        verbose_name='resultado',
    )
    proxima_revision = models.DateField(
        null=True, blank=True, verbose_name='proxima revision'
    )
    realizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revisiones_equipo_realizadas',
        verbose_name='realizado por',
    )
    observaciones = models.TextField(blank=True, verbose_name='observaciones')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'revision de equipo'
        verbose_name_plural = 'revisiones de equipo'
        ordering = ['-fecha', '-created_at']
        indexes = [
            models.Index(fields=['empresa', 'resultado']),
            models.Index(fields=['fecha']),
        ]

    def __str__(self):
        return f'Revision {self.equipo} - {self.fecha}'

    @property
    def badge_resultado(self):
        mapping = {
            'conforme': 'badge-success',
            'observaciones': 'badge-warning',
            'no_conforme': 'badge-danger',
            'reparado': 'badge-moderate',
        }
        return mapping.get(self.resultado, 'badge-secondary')


class MantenimientoEquipo(AuditFieldsMixin, models.Model):

    class TipoMantenimiento(models.TextChoices):
        PREVENTIVO = 'preventivo', 'Preventivo'
        CORRECTIVO = 'correctivo', 'Correctivo'
        PREDICTIVO = 'predictivo', 'Predictivo'

    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='mantenimientos_equipo',
        verbose_name='empresa',
    )
    equipo = models.ForeignKey(
        EquipoTrabajo,
        on_delete=models.CASCADE,
        related_name='mantenimientos',
        verbose_name='equipo',
    )
    fecha = models.DateField(verbose_name='fecha de mantenimiento')
    tipo = models.CharField(
        max_length=20,
        choices=TipoMantenimiento.choices,
        default=TipoMantenimiento.PREVENTIVO,
        verbose_name='tipo de mantenimiento',
    )
    descripcion = models.TextField(verbose_name='descripcion del trabajo realizado')
    costo = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name='costo estimado'
    )
    realizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mantenimientos_equipo_realizados',
        verbose_name='realizado por',
    )
    proveedor = models.CharField(max_length=200, blank=True, verbose_name='proveedor externo')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'mantenimiento de equipo'
        verbose_name_plural = 'mantenimientos de equipo'
        ordering = ['-fecha', '-created_at']
        indexes = [
            models.Index(fields=['empresa', 'tipo']),
            models.Index(fields=['fecha']),
        ]

    def __str__(self):
        return f'{self.get_tipo_display()} - {self.equipo} - {self.fecha}'
