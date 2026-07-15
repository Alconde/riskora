from django.conf import settings
from django.db import models
from apps.core.mixins import AuditFieldsMixin


class PlantillaInspeccion(AuditFieldsMixin, models.Model):

    class Categoria(models.TextChoices):
        SEGURIDAD = 'seguridad', 'Seguridad'
        SALUD = 'salud', 'Salud laboral'
        MEDIO_AMBIENTE = 'medio_ambiente', 'Medio ambiente'
        MAQUINARIA = 'maquinaria', 'Maquinaria'
        INSTALACIONES = 'instalaciones', 'Instalaciones'
        EPI = 'epi', 'EPIs'
        OTRO = 'otro', 'Otro'

    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='plantillas_inspeccion',
        verbose_name='empresa',
    )
    nombre = models.CharField(max_length=200, verbose_name='nombre')
    descripcion = models.TextField(blank=True, verbose_name='descripcion')
    categoria = models.CharField(
        max_length=20,
        choices=Categoria.choices,
        default=Categoria.SEGURIDAD,
        verbose_name='categoria',
    )
    activa = models.BooleanField(default=True, verbose_name='activa')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'plantilla de inspeccion'
        verbose_name_plural = 'plantillas de inspeccion'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class PlantillaInspeccionItem(AuditFieldsMixin, models.Model):
    plantilla = models.ForeignKey(
        PlantillaInspeccion,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='plantilla',
    )
    orden = models.PositiveIntegerField(default=0, verbose_name='orden')
    descripcion = models.TextField(verbose_name='que se inspecciona')

    class Meta:
        verbose_name = 'item de plantilla'
        verbose_name_plural = 'items de plantilla'
        ordering = ['orden']

    def __str__(self):
        return f'{self.orden}. {self.descripcion[:60]}'


class Inspeccion(AuditFieldsMixin, models.Model):

    class Estado(models.TextChoices):
        PLANIFICADA = 'planificada', 'Planificada'
        EN_CURSO = 'en_curso', 'En curso'
        COMPLETADA = 'completada', 'Completada'
        CON_NC = 'con_nc', 'Con no conformidades'

    class ResultadoGeneral(models.TextChoices):
        CONFORME = 'conforme', 'Conforme'
        NO_CONFORME = 'no_conforme', 'No conforme'
        PARCIAL = 'parcial', 'Parcialmente conforme'

    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='inspecciones',
        verbose_name='empresa',
    )
    plantilla = models.ForeignKey(
        PlantillaInspeccion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inspecciones',
        verbose_name='plantilla',
    )
    centro_trabajo = models.ForeignKey(
        'workcenters.WorkCenter',
        on_delete=models.CASCADE,
        related_name='inspecciones',
        verbose_name='centro de trabajo',
    )
    inspector = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='inspecciones_realizadas',
        verbose_name='inspector',
    )
    fecha_inspeccion = models.DateField(verbose_name='fecha de inspeccion')
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PLANIFICADA,
        verbose_name='estado',
    )
    resultado_general = models.CharField(
        max_length=20,
        choices=ResultadoGeneral.choices,
        blank=True,
        verbose_name='resultado general',
    )
    observaciones = models.TextField(blank=True, verbose_name='observaciones')
    fotos = models.FileField(
        upload_to='inspecciones/fotos/',
        blank=True,
        verbose_name='fotos evidencia',
    )
    nc_generadas = models.BooleanField(
        default=False, verbose_name='NCs generadas'
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='inspecciones_creadas',
        verbose_name='creado por',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'inspeccion'
        verbose_name_plural = 'inspecciones'
        ordering = ['-fecha_inspeccion', '-created_at']
        indexes = [
            models.Index(fields=['empresa', 'estado']),
            models.Index(fields=['empresa', 'centro_trabajo']),
            models.Index(fields=['fecha_inspeccion']),
        ]

    def __str__(self):
        return f'INS-{self.pk:04d} - {self.centro_trabajo}'

    @property
    def total_items(self):
        return self.items.count()

    @property
    def items_conforme(self):
        return self.items.filter(resultado='conforme').count()

    @property
    def items_no_conforme(self):
        return self.items.filter(resultado='no_conforme').count()

    @property
    def items_na(self):
        return self.items.filter(resultado='na').count()

    @property
    def porcentaje_cumplimiento(self):
        total = self.total_items - self.items_na
        if total == 0:
            return 100
        return round((self.items_conforme / total) * 100)

    @property
    def badge_estado(self):
        mapping = {
            'planificada': 'badge-secondary',
            'en_curso': 'badge-moderate',
            'completada': 'badge-success',
            'con_nc': 'badge-danger',
        }
        return mapping.get(self.estado, 'badge-secondary')

    @property
    def badge_resultado(self):
        mapping = {
            'conforme': 'badge-success',
            'no_conforme': 'badge-danger',
            'parcial': 'badge-warning',
        }
        return mapping.get(self.resultado_general, 'badge-secondary')


class ItemInspeccion(AuditFieldsMixin, models.Model):

    class Resultado(models.TextChoices):
        CONFORME = 'conforme', 'Conforme'
        NO_CONFORME = 'no_conforme', 'No conforme'
        NA = 'na', 'No aplica'

    inspeccion = models.ForeignKey(
        Inspeccion,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='inspeccion',
    )
    orden = models.PositiveIntegerField(default=0, verbose_name='orden')
    descripcion = models.TextField(verbose_name='que se inspecciona')
    resultado = models.CharField(
        max_length=20,
        choices=Resultado.choices,
        blank=True,
        verbose_name='resultado',
    )
    observaciones = models.TextField(blank=True, verbose_name='observaciones')
    foto = models.FileField(
        upload_to='inspecciones/items/',
        blank=True,
        verbose_name='foto evidencia',
    )
    no_conformidad = models.ForeignKey(
        'corrective_actions.NoConformidad',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items_inspeccion',
        verbose_name='no conformidad generada',
    )

    class Meta:
        verbose_name = 'item de inspeccion'
        verbose_name_plural = 'items de inspeccion'
        ordering = ['orden']
        indexes = [
            models.Index(fields=['inspeccion', 'resultado']),
        ]

    def __str__(self):
        return f'{self.orden}. {self.descripcion[:60]}'

    @property
    def badge_resultado(self):
        mapping = {
            'conforme': 'badge-success',
            'no_conforme': 'badge-danger',
            'na': 'badge-secondary',
        }
        return mapping.get(self.resultado, 'badge-secondary')
