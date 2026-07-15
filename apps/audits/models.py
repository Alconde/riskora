from django.conf import settings
from django.db import models
from apps.core.mixins import AuditFieldsMixin


class ProgramaAuditoria(AuditFieldsMixin, models.Model):

    class Estado(models.TextChoices):
        BORRADOR = 'borrador', 'Borrador'
        APROBADO = 'aprobado', 'Aprobado'
        EN_EJECUCION = 'en_ejecucion', 'En ejecución'
        COMPLETADO = 'completado', 'Completado'

    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='programas_auditoria',
        verbose_name='empresa',
    )
    anio = models.PositiveIntegerField('año del programa')
    version = models.CharField('versión', max_length=20, default='1.0')
    alcance = models.TextField(
        'alcance',
        blank=True,
        default='',
        help_text='Cláusulas ISO 45001 incluidas en el programa anual',
    )
    aprobado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='programas_aprobados',
        verbose_name='aprobado por',
    )
    fecha_aprobacion = models.DateField('fecha de aprobación', null=True, blank=True)
    estado = models.CharField(
        'estado',
        max_length=20,
        choices=Estado.choices,
        default=Estado.BORRADOR,
    )
    notas = models.TextField('observaciones', blank=True)

    created_at = models.DateTimeField('creado el', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado el', auto_now=True)

    class Meta:
        verbose_name = 'programa de auditoría'
        verbose_name_plural = 'programas de auditoría'
        ordering = ['-anio', '-created_at']
        unique_together = ('empresa', 'anio')

    def __str__(self):
        return f'Programa {self.anio} — {self.empresa}'

    @property
    def total_auditorias(self):
        return self.auditorias.count()

    @property
    def auditorias_completadas(self):
        return self.auditorias.filter(estado='completada').count()

    @property
    def porcentaje_avance(self):
        total = self.total_auditorias
        if total == 0:
            return 0
        return round((self.auditorias_completadas / total) * 100)

    @property
    def badge_estado(self):
        return {
            'borrador': 'badge-secondary',
            'aprobado': 'badge-info',
            'en_ejecucion': 'badge-warning',
            'completado': 'badge-success',
        }.get(self.estado, 'badge-secondary')


class AuditoriaInterna(AuditFieldsMixin, models.Model):

    class Estado(models.TextChoices):
        PLANIFICADA = 'planificada', 'Planificada'
        EN_CURSO = 'en_curso', 'En curso'
        COMPLETADA = 'completada', 'Completada'
        INFORME_PENDIENTE = 'informe_pendiente', 'Informe pendiente'
        CERRADA = 'cerrada', 'Cerrada'

    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='auditorias_internas',
        verbose_name='empresa',
    )
    programa = models.ForeignKey(
        ProgramaAuditoria,
        on_delete=models.CASCADE,
        related_name='auditorias',
        verbose_name='programa de auditoría',
    )
    titulo = models.CharField('título de la auditoría', max_length=255)
    descripcion = models.TextField('descripción / alcance', blank=True)

    fecha_planificada = models.DateField('fecha planificada')
    fecha_realizacion = models.DateField('fecha de realización', null=True, blank=True)

    equipo_auditor = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='auditorias_equipo',
        verbose_name='equipo auditor',
    )
    lider_auditoria = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='lider_auditorias',
        verbose_name='líder de auditoría',
    )
    auditados = models.TextField(
        'personas auditadas / áreas',
        blank=True,
        default='',
    )

    estado = models.CharField(
        'estado',
        max_length=25,
        choices=Estado.choices,
        default=Estado.PLANIFICADA,
    )
    observaciones = models.TextField('observaciones generales', blank=True)

    created_at = models.DateTimeField('creado el', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado el', auto_now=True)

    class Meta:
        verbose_name = 'auditoría interna'
        verbose_name_plural = 'auditorías internas'
        ordering = ['-fecha_planificada', '-created_at']
        indexes = [
            models.Index(fields=['empresa', 'estado']),
            models.Index(fields=['empresa', 'fecha_planificada']),
            models.Index(fields=['programa']),
        ]

    def __str__(self):
        return f'AUD-{self.pk:04d} — {self.titulo}'

    @property
    def total_checklist(self):
        return self.checklist.count()

    @property
    def conformes(self):
        return self.checklist.filter(conformidad='conforme').count()

    @property
    def no_conformes(self):
        return self.checklist.filter(conformidad='no_conforme').count()

    @property
    def observaciones_count(self):
        return self.checklist.filter(conformidad='observacion').count()

    @property
    def porcentaje_cumplimiento(self):
        evaluados = self.checklist.exclude(conformidad='').exclude(conformidad='no_aplica').count()
        if evaluados == 0:
            return 0
        return round((self.conformes / evaluados) * 100)

    @property
    def tiene_informe(self):
        return hasattr(self, 'informe') and self.informe is not None

    @property
    def badge_estado(self):
        return {
            'planificada': 'badge-secondary',
            'en_curso': 'badge-warning',
            'completada': 'badge-info',
            'informe_pendiente': 'badge-moderate',
            'cerrada': 'badge-success',
        }.get(self.estado, 'badge-secondary')


class ChecklistAuditoria(AuditFieldsMixin, models.Model):

    class Conformidad(models.TextChoices):
        CONFORME = 'conforme', 'Conforme'
        NO_CONFORME = 'no_conforme', 'No conforme'
        OBSERVACION = 'observacion', 'Observación'
        NO_APLICA = 'no_aplica', 'No aplica'

    auditoria = models.ForeignKey(
        AuditoriaInterna,
        on_delete=models.CASCADE,
        related_name='checklist',
        verbose_name='auditoría',
    )
    clausula_iso = models.CharField(
        'cláusula ISO 45001',
        max_length=20,
        help_text='ej: 4.1, 5.2, 8.1.2, 9.2.1',
    )
    seccion = models.CharField(
        'sección',
        max_length=200,
        blank=True,
        default='',
        help_text='Nombre de la sección de la cláusula',
    )
    requisito = models.TextField('requisito / pregunta de auditoría')
    evidencia_requerida = models.TextField(
        'evidencia requerida',
        blank=True,
        default='',
        help_text='Qué evidencia debe presentarse',
    )
    conformidad = models.CharField(
        'conformidad',
        max_length=20,
        choices=Conformidad.choices,
        blank=True,
        default='',
    )
    hallazgo = models.TextField(
        'hallazgo / descripción del resultado',
        blank=True,
        default='',
    )
    evidencia_encontrada = models.TextField(
        'evidencia encontrada',
        blank=True,
        default='',
    )
    accion_correctiva = models.ForeignKey(
        'corrective_actions.NoConformidad',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='checklist_auditoria',
        verbose_name='no conformidad generada',
    )
    responsable_seguimiento = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='checklist_seguimiento',
        verbose_name='responsable de seguimiento',
    )
    plazo_cierre = models.DateField('plazo de cierre', null=True, blank=True)
    cerrado = models.BooleanField('cerrado', default=False)
    fecha_cierre = models.DateField('fecha de cierre', null=True, blank=True)

    created_at = models.DateTimeField('creado el', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado el', auto_now=True)

    class Meta:
        verbose_name = 'item de checklist de auditoría'
        verbose_name_plural = 'items de checklist de auditoría'
        ordering = ['clausula_iso', 'seccion']
        indexes = [
            models.Index(fields=['auditoria', 'conformidad']),
            models.Index(fields=['clausula_iso']),
        ]

    def __str__(self):
        return f'{self.clausula_iso} — {self.requisito[:60]}'

    @property
    def badge_conformidad(self):
        return {
            'conforme': 'badge-success',
            'no_conforme': 'badge-danger',
            'observacion': 'badge-warning',
            'no_aplica': 'badge-secondary',
        }.get(self.conformidad, 'badge-secondary')

    @property
    def tiene_nc(self):
        return self.accion_correctiva is not None


class InformeAuditoria(AuditFieldsMixin, models.Model):

    auditoria = models.OneToOneField(
        AuditoriaInterna,
        on_delete=models.CASCADE,
        related_name='informe',
        verbose_name='auditoría',
    )
    resumen_ejecutivo = models.TextField('resumen ejecutivo')
    hallazgos_resumen = models.TextField('resumen de hallazgos')
    puntos_fuertes = models.TextField('puntos fuertes', blank=True, default='')
    oportunidades_mejora = models.TextField('oportunidades de mejora', blank=True, default='')
    recomendaciones = models.TextField('recomendaciones', blank=True, default='')
    fecha_informe = models.DateField('fecha del informe')
    elaborado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='informes_elaborados',
        verbose_name='elaborado por',
    )
    aprobado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='informes_aprobados',
        verbose_name='aprobado por',
    )
    fecha_aprobacion = models.DateField('fecha de aprobación', null=True, blank=True)
    archivo_pdf = models.FileField(
        'informe PDF',
        upload_to='auditorias/informes/',
        blank=True,
    )
    created_at = models.DateTimeField('creado el', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado el', auto_now=True)

    class Meta:
        verbose_name = 'informe de auditoría'
        verbose_name_plural = 'informes de auditoría'
        ordering = ['-fecha_informe', '-created_at']

    def __str__(self):
        return f'Informe — {self.auditoria}'
