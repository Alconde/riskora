from django.conf import settings
from django.db import models
from django.utils import timezone
from apps.core.mixins import AuditFieldsMixin


class CatalogoEPI(AuditFieldsMixin, models.Model):

    class Categoria(models.TextChoices):
        CABEZA = 'cabeza', 'Proteccion de la cabeza'
        MANOS = 'manos', 'Proteccion de las manos'
        PIES = 'pies', 'Proteccion de los pies'
        OJOS = 'ojos', 'Proteccion ocular'
        OIDOS = 'oidos', 'Proteccion auditiva'
        RESPIRATORIA = 'respiratoria', 'Proteccion respiratoria'
        CORPORAL = 'corporal', 'Proteccion corporal'
        OTRO = 'otro', 'Otro'

    nombre = models.CharField(max_length=200, verbose_name='nombre')
    categoria = models.CharField(
        max_length=20,
        choices=Categoria.choices,
        default=Categoria.CABEZA,
        verbose_name='categoria',
    )
    riesgos_proteccion = models.TextField(
        verbose_name='riesgos que protege',
        help_text='Describe los riesgos frente a los que protege este EPI.',
    )
    norma_eu = models.CharField(
        max_length=100,
        verbose_name='norma UNE / EN',
        help_text='Norma europea que debe cumplir (ej: EN 166, EN 388, EN ISO 20345).',
    )
    descripcion = models.TextField(blank=True, verbose_name='descripcion')
    imagen = models.FileField(
        upload_to='epis/catalogo/',
        blank=True,
        verbose_name='imagen',
    )
    activo = models.BooleanField(default=True, verbose_name='activo')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'catalogo de EPI'
        verbose_name_plural = 'catalogo de EPIs'
        ordering = ['categoria', 'nombre']

    def __str__(self):
        return f'{self.get_categoria_display()} - {self.nombre}'


class EPI(AuditFieldsMixin, models.Model):

    class Estado(models.TextChoices):
        DISPONIBLE = 'disponible', 'Disponible'
        ASIGNADO = 'asignado', 'Asignado'
        EN_MANTENIMIENTO = 'en_mantenimiento', 'En mantenimiento'
        RETIRADO = 'retirado', 'Retirado'

    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='epis',
        verbose_name='empresa',
    )
    catalogo = models.ForeignKey(
        CatalogoEPI,
        on_delete=models.CASCADE,
        related_name='epis',
        null=True,
        blank=True,
        verbose_name='catalogo de EPI',
    )
    marca = models.CharField(max_length=100, verbose_name='marca')
    modelo = models.CharField(max_length=100, verbose_name='modelo')
    numero_serie = models.CharField(
        max_length=100, blank=True, verbose_name='numero de serie'
    )
    vida_util_meses = models.PositiveIntegerField(
        default=12, verbose_name='vida util (meses)'
    )
    precio = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name='precio unitario'
    )
    proveedor = models.CharField(max_length=200, blank=True, verbose_name='proveedor')
    fecha_compra = models.DateField(null=True, blank=True, verbose_name='fecha de compra')
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.DISPONIBLE,
        verbose_name='estado',
    )
    activo = models.BooleanField(default=True, verbose_name='activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'EPI'
        verbose_name_plural = 'EPIs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['empresa', 'estado']),
            models.Index(fields=['empresa', 'catalogo']),
        ]

    def __str__(self):
        return f'{self.catalogo.nombre} - {self.marca} {self.modelo}'

    @property
    def badge_estado(self):
        mapping = {
            'disponible': 'badge-success',
            'asignado': 'badge-moderate',
            'en_mantenimiento': 'badge-warning',
            'retirado': 'badge-secondary',
        }
        return mapping.get(self.estado, 'badge-secondary')

    @property
    def total_entregas(self):
        return self.entregas.count()

    @property
    def entrega_activa(self):
        return self.entregas.filter(estado='activo').first()


class EntregaEPI(AuditFieldsMixin, models.Model):

    class Estado(models.TextChoices):
        ACTIVO = 'activo', 'Activo'
        DEVUELTO = 'devuelto', 'Devuelto'
        CADUCADO = 'caducado', 'Caducado'
        REEMPLAZADO = 'reemplazado', 'Reemplazado'

    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='entregas_epi',
        verbose_name='empresa',
    )
    epi = models.ForeignKey(
        EPI,
        on_delete=models.CASCADE,
        related_name='entregas',
        verbose_name='EPI',
    )
    trabajador = models.ForeignKey(
        'workers.Worker',
        on_delete=models.CASCADE,
        related_name='entregas_epi',
        verbose_name='trabajador',
    )
    fecha_entrega = models.DateField(verbose_name='fecha de entrega')
    fecha_caducidad = models.DateField(
        null=True, blank=True, verbose_name='fecha de caducidad'
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ACTIVO,
        verbose_name='estado',
    )
    motivo_devolucion = models.TextField(
        blank=True, verbose_name='motivo de devolucion'
    )
    entregado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='entregas_epi_realizadas',
        verbose_name='entregado por',
    )
    firma_trabajador = models.BooleanField(
        default=False, verbose_name='firma del trabajador'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'entrega de EPI'
        verbose_name_plural = 'entregas de EPI'
        ordering = ['-fecha_entrega', '-created_at']
        indexes = [
            models.Index(fields=['empresa', 'estado']),
            models.Index(fields=['empresa', 'trabajador']),
            models.Index(fields=['fecha_caducidad']),
        ]

    def __str__(self):
        return f'{self.epi} -> {self.trabajador}'

    @property
    def badge_estado(self):
        mapping = {
            'activo': 'badge-success',
            'devuelto': 'badge-secondary',
            'caducado': 'badge-danger',
            'reemplazado': 'badge-warning',
        }
        return mapping.get(self.estado, 'badge-secondary')

    @property
    def esta_caducada(self):
        if not self.fecha_caducidad:
            return False
        return self.fecha_caducidad < timezone.localdate()

    @property
    def dias_hasta_caducidad(self):
        if not self.fecha_caducidad:
            return None
        delta = self.fecha_caducidad - timezone.localdate()
        return delta.days


class InspeccionEPI(AuditFieldsMixin, models.Model):

    class Resultado(models.TextChoices):
        BUENO = 'bueno', 'Buen estado'
        REGULAR = 'regular', 'Estado regular'
        MALO = 'malo', 'Mal estado'
        RECHAZADO = 'rechazado', 'Rechazado'

    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='inspecciones_epi',
        verbose_name='empresa',
    )
    epi = models.ForeignKey(
        EPI,
        on_delete=models.CASCADE,
        related_name='inspecciones',
        verbose_name='EPI',
    )
    entrega = models.ForeignKey(
        EntregaEPI,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inspecciones',
        verbose_name='entrega asociada',
    )
    fecha = models.DateField(verbose_name='fecha de inspeccion')
    resultado = models.CharField(
        max_length=20,
        choices=Resultado.choices,
        default=Resultado.BUENO,
        verbose_name='resultado',
    )
    observaciones = models.TextField(blank=True, verbose_name='observaciones')
    inspeccionado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inspecciones_epi_realizadas',
        verbose_name='inspeccionado por',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'inspeccion de EPI'
        verbose_name_plural = 'inspecciones de EPI'
        ordering = ['-fecha', '-created_at']
        indexes = [
            models.Index(fields=['empresa', 'resultado']),
            models.Index(fields=['fecha']),
        ]

    def __str__(self):
        return f'Inspeccion {self.epi} - {self.fecha}'

    @property
    def badge_resultado(self):
        mapping = {
            'bueno': 'badge-success',
            'regular': 'badge-warning',
            'malo': 'badge-danger',
            'rechazado': 'badge-danger',
        }
        return mapping.get(self.resultado, 'badge-secondary')


class ProcedimientoEntrega(AuditFieldsMixin, models.Model):
    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='procedimientos_epi',
        verbose_name='empresa',
    )
    titulo = models.CharField(max_length=200, verbose_name='titulo')
    descripcion = models.TextField(blank=True, verbose_name='descripcion')
    archivo = models.FileField(
        upload_to='epis/procedimientos/',
        verbose_name='archivo del procedimiento',
    )
    version = models.CharField(max_length=20, default='1.0', verbose_name='version')
    activo = models.BooleanField(default=True, verbose_name='activo')
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='procedimientos_epi',
        verbose_name='subido por',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'procedimiento de entrega de EPI'
        verbose_name_plural = 'procedimientos de entrega de EPI'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.titulo} v{self.version}'


class FirmaEntrega(AuditFieldsMixin, models.Model):
    class EstadoFirma(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente de firma'
        FIRMADO = 'firmado', 'Firmado'
        NO_APLICA = 'no_aplica', 'No aplica'

    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='firmas_epi',
        verbose_name='empresa',
    )
    entrega = models.OneToOneField(
        EntregaEPI,
        on_delete=models.CASCADE,
        related_name='firma',
        verbose_name='entrega',
    )
    trabajador = models.ForeignKey(
        'workers.Worker',
        on_delete=models.CASCADE,
        related_name='firmas_epi',
        verbose_name='trabajador',
    )
    estado_firma = models.CharField(
        max_length=20,
        choices=EstadoFirma.choices,
        default=EstadoFirma.PENDIENTE,
        verbose_name='estado de firma',
    )
    archivo_firmado = models.FileField(
        upload_to='epis/firmas/',
        blank=True,
        verbose_name='acuse firmado (PDF)',
    )
    fecha_firma = models.DateField(
        null=True, blank=True, verbose_name='fecha de firma'
    )
    notas = models.TextField(blank=True, verbose_name='notas')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'firma de entrega de EPI'
        verbose_name_plural = 'firmas de entrega de EPI'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['empresa', 'estado_firma']),
            models.Index(fields=['empresa', 'trabajador']),
        ]

    def __str__(self):
        return f'Firma: {self.trabajador} - {self.get_estado_firma_display()}'

    @property
    def badge_estado_firma(self):
        mapping = {
            'pendiente': 'badge-warning',
            'firmado': 'badge-success',
            'no_aplica': 'badge-secondary',
        }
        return mapping.get(self.estado_firma, 'badge-secondary')
