from django.conf import settings
from django.db import models

from apps.core.mixins import AuditFieldsMixin


class NoConformidad(AuditFieldsMixin, models.Model):

    class Fuente(models.TextChoices):
        INTERNA = 'interna', 'Interna'
        EXTERNA = 'externa', 'Externa'
        AUDITORIA = 'auditoria', 'Auditoria'
        RECLAMACION = 'reclamacion', 'Reclamacion'
        INSPECCION = 'inspeccion', 'Inspeccion'
        ACCIDENTE = 'accidente', 'Accidente'

    class Gravedad(models.TextChoices):
        MENOR = 'menor', 'Menor'
        MODERADA = 'moderada', 'Moderada'
        IMPORTANTE = 'importante', 'Importante'
        CRITICA = 'critica', 'Critica'

    class Estado(models.TextChoices):
        ABIERTA = 'abierta', 'Abierta'
        EN_INVESTIGACION = 'en_investigacion', 'En investigacion'
        EN_TRATAMIENTO = 'en_tratamiento', 'En tratamiento'
        RESUELTA = 'resuelta', 'Resuelta'
        CERRADA = 'cerrada', 'Cerrada'
        CANCELADA = 'cancelada', 'Cancelada'

    class MetodoCausaRaiz(models.TextChoices):
        CINCO_PORQUES = '_5_porques', '5 Porques'
        ISHIKAWA = 'ishikawa', 'Ishikawa (Espina de pez)'
        OTRO = 'otro', 'Otro'

    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='no_conformidades',
        verbose_name='empresa',
    )
    codigo = models.CharField(max_length=30, unique=True, verbose_name='codigo')
    titulo = models.CharField(max_length=200, verbose_name='titulo')
    descripcion = models.TextField(verbose_name='descripcion')

    fuente = models.CharField(
        max_length=20,
        choices=Fuente.choices,
        default=Fuente.INTERNA,
        verbose_name='fuente',
    )
    gravedad = models.CharField(
        max_length=20,
        choices=Gravedad.choices,
        default=Gravedad.MODERADA,
        verbose_name='gravedad',
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ABIERTA,
        verbose_name='estado',
    )

    detectado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='nc_detectadas',
        verbose_name='detectado por',
    )
    fecha_deteccion = models.DateField(verbose_name='fecha de deteccion')

    centro_trabajo = models.ForeignKey(
        'workcenters.WorkCenter',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='no_conformidades',
        verbose_name='centro de trabajo',
    )
    trabajador = models.ForeignKey(
        'workers.Worker',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='no_conformidades',
        verbose_name='trabajador',
    )
    ubicacion = models.CharField(
        max_length=200, blank=True, verbose_name='ubicacion especifica'
    )

    causa_raiz = models.TextField(blank=True, verbose_name='causa raiz')
    metodo_causa_raiz = models.CharField(
        max_length=20,
        choices=MetodoCausaRaiz.choices,
        default=MetodoCausaRaiz.CINCO_PORQUES,
        verbose_name='metodo de analisis',
    )

    evidencias = models.TextField(blank=True, verbose_name='evidencias')
    archivo_evidencia = models.FileField(
        upload_to='corrective_actions/evidencias/',
        blank=True,
        verbose_name='archivo de evidencia',
    )

    fecha_limite_resolucion = models.DateField(
        verbose_name='fecha limite de resolucion'
    )
    resuelta_en = models.DateField(
        null=True, blank=True, verbose_name='fecha de resolucion'
    )

    verificada = models.BooleanField(default=False, verbose_name='verificada')
    fecha_verificacion = models.DateField(
        null=True, blank=True, verbose_name='fecha de verificacion'
    )
    verificada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='nc_verificadas',
        verbose_name='verificada por',
    )
    notas_verificacion = models.TextField(
        blank=True, verbose_name='notas de verificacion'
    )

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='nc_creadas',
        verbose_name='creado por',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'no conformidad'
        verbose_name_plural = 'no conformidades'
        ordering = ['-fecha_deteccion', '-created_at']
        indexes = [
            models.Index(fields=['empresa', 'estado']),
            models.Index(fields=['empresa', 'gravedad']),
            models.Index(fields=['fecha_limite_resolucion']),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.titulo}'

    @property
    def esta_vencida(self):
        from django.utils import timezone
        return (
            self.estado in (self.Estado.ABIERTA, self.Estado.EN_INVESTIGACION, self.Estado.EN_TRATAMIENTO)
            and self.fecha_limite_resolucion
            and self.fecha_limite_resolucion < timezone.localdate()
        )

    @property
    def dias_restantes(self):
        from django.utils import timezone
        if not self.fecha_limite_resolucion:
            return None
        delta = self.fecha_limite_resolucion - timezone.localdate()
        return delta.days

    @property
    def badge_estado(self):
        mapping = {
            'abierta': 'badge-danger',
            'en_investigacion': 'badge-warning',
            'en_tratamiento': 'badge-moderate',
            'resuelta': 'badge-success',
            'cerrada': 'badge-success',
            'cancelada': 'badge-secondary',
        }
        return mapping.get(self.estado, 'badge-secondary')

    @property
    def badge_gravedad(self):
        mapping = {
            'menor': 'badge-muy_bajo',
            'moderada': 'badge-bajo',
            'importante': 'badge-alto',
            'critica': 'badge-muy_alto',
        }
        return mapping.get(self.gravedad, 'badge-secondary')


class AccionCorrectiva(AuditFieldsMixin, models.Model):

    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        EN_PROGRESO = 'en_progreso', 'En progreso'
        COMPLETADA = 'completada', 'Completada'
        CANCELADA = 'cancelada', 'Cancelada'

    no_conformidad = models.ForeignKey(
        NoConformidad,
        on_delete=models.CASCADE,
        related_name='acciones_correctivas',
        verbose_name='no conformidad',
    )
    descripcion = models.TextField(verbose_name='descripcion de la accion')
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acciones_correctivas',
        verbose_name='responsable',
    )
    fecha_limite = models.DateField(verbose_name='fecha limite')
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        verbose_name='estado',
    )
    fecha_ejecucion = models.DateField(
        null=True, blank=True, verbose_name='fecha de ejecucion'
    )
    evidencia_implementacion = models.TextField(
        blank=True, verbose_name='evidencia de implementacion'
    )
    archivo_evidencia = models.FileField(
        upload_to='corrective_actions/acciones/',
        blank=True,
        verbose_name='archivo de evidencia',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'accion correctiva'
        verbose_name_plural = 'acciones correctivas'
        ordering = ['fecha_limite', '-created_at']
        indexes = [
            models.Index(fields=['no_conformidad', 'estado']),
            models.Index(fields=['fecha_limite']),
        ]

    def __str__(self):
        return f'AC-{self.pk:04d} -> {self.no_conformidad.codigo}'

    @property
    def esta_vencida(self):
        from django.utils import timezone
        return (
            self.estado in (self.Estado.PENDIENTE, self.Estado.EN_PROGRESO)
            and self.fecha_limite
            and self.fecha_limite < timezone.localdate()
        )

    @property
    def badge_estado(self):
        mapping = {
            'pendiente': 'badge-warning',
            'en_progreso': 'badge-moderate',
            'completada': 'badge-success',
            'cancelada': 'badge-secondary',
        }
        return mapping.get(self.estado, 'badge-secondary')


class AccionPreventiva(AuditFieldsMixin, models.Model):

    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        EN_PROGRESO = 'en_progreso', 'En progreso'
        COMPLETADA = 'completada', 'Completada'
        CANCELADA = 'cancelada', 'Cancelada'

    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='acciones_preventivas',
        verbose_name='empresa',
    )
    no_conformidad_origen = models.ForeignKey(
        NoConformidad,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acciones_preventivas',
        verbose_name='no conformidad de origen',
    )
    titulo = models.CharField(max_length=200, verbose_name='titulo')
    descripcion = models.TextField(verbose_name='descripcion')
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acciones_preventivas',
        verbose_name='responsable',
    )
    fecha_limite = models.DateField(verbose_name='fecha limite')
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        verbose_name='estado',
    )
    fecha_ejecucion = models.DateField(
        null=True, blank=True, verbose_name='fecha de ejecucion'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'accion preventiva'
        verbose_name_plural = 'acciones preventivas'
        ordering = ['fecha_limite', '-created_at']
        indexes = [
            models.Index(fields=['empresa', 'estado']),
            models.Index(fields=['fecha_limite']),
        ]

    def __str__(self):
        return f'{self.titulo}'

    @property
    def esta_vencida(self):
        from django.utils import timezone
        return (
            self.estado in (self.Estado.PENDIENTE, self.Estado.EN_PROGRESO)
            and self.fecha_limite
            and self.fecha_limite < timezone.localdate()
        )

    @property
    def badge_estado(self):
        mapping = {
            'pendiente': 'badge-warning',
            'en_progreso': 'badge-moderate',
            'completada': 'badge-success',
            'cancelada': 'badge-secondary',
        }
        return mapping.get(self.estado, 'badge-secondary')
