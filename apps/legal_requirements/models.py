from django.conf import settings
from django.db import models


class NormativaLegal(models.Model):

    class Tipo(models.TextChoices):
        LEY = 'ley', 'Ley'
        REAL_DECRETO = 'real_decreto', 'Real Decreto'
        RD_TO = 'rd_to', 'Real Decreto - Texto Ordinado'
        ORDEN = 'orden', 'Orden Ministerial'
        INSTRUCTION = 'instruccion', 'Instrucción'
        REGLO = 'reglamento', 'Reglamento'
        NTP = 'ntp', 'Nota Técnica de Prevención'
        OTRA = 'otra', 'Otra normativa'

    class Ambito(models.TextChoices):
        ESTATAL = 'estatal', 'Estatal'
        AUTONOMICO = 'autonomico', 'Autonómico'
        LOCAL = 'local', 'Local'
        EUROPEO = 'europeo', 'Europeo'
        INTERNACIONAL = 'internacional', 'Internacional'

    nombre = models.CharField('nombre / título', max_length=500)
    tipo = models.CharField('tipo de normativa', max_length=30, choices=Tipo.choices)
    numero = models.CharField(
        'número / referencia',
        max_length=100,
        blank=True,
        default='',
        help_text='ej: 31/1995, 39/1997',
    )
    ambito = models.CharField(
        'ámbito',
        max_length=30,
        choices=Ambito.choices,
        default=Ambito.ESTATAL,
    )
    comunidad_autonoma = models.CharField(
        'comunidad autónoma',
        max_length=100,
        blank=True,
        default='',
        help_text='Solo si es normativa autonómica',
    )
    fecha_publicacion = models.DateField('fecha de publicación', null=True, blank=True)
    fecha_vigencia = models.DateField('fecha de entrada en vigor', null=True, blank=True)
    fecha_fin_vigencia = models.DateField('fecha fin de vigencia', null=True, blank=True)
    boe_enlace = models.URLField(
        'enlace BOE / normativa',
        blank=True,
        default='',
        help_text='Enlace al texto completo en BOE o fuente oficial',
    )
    resumen = models.TextField(
        'resumen',
        blank=True,
        default='',
        help_text='Resumen de las principales disposiciones',
    )
    activa = models.BooleanField('normativa activa', default=True)
    notas_internas = models.TextField('notas internas', blank=True, default='')

    created_at = models.DateTimeField('creado el', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado el', auto_now=True)

    class Meta:
        verbose_name = 'normativa legal'
        verbose_name_plural = 'normativa legal'
        ordering = ['-fecha_publicacion', 'numero']
        indexes = [
            models.Index(fields=['tipo', 'activa']),
            models.Index(fields=['ambito']),
        ]

    def __str__(self):
        parts = []
        if self.tipo:
            parts.append(self.get_tipo_display())
        if self.numero:
            parts.append(f'n.º {self.numero}')
        if self.fecha_publicacion:
            parts.append(f'({self.fecha_publicacion.year})')
        return ' '.join(parts) if parts else self.nombre[:80]

    @property
    def referencia_completa(self):
        return f'{self.get_tipo_display()} n.º {self.numero}/{self.fecha_publicacion.year if self.fecha_publicacion else "s/f"}'

    @property
    def badge_ambito(self):
        return {
            'estatal': 'badge-info',
            'autonomico': 'badge-warning',
            'local': 'badge-secondary',
            'europeo': 'badge-primary',
            'internacional': 'badge-moderate',
        }.get(self.ambito, 'badge-secondary')

    @property
    def vigente(self):
        from datetime import date
        hoy = date.today()
        if not self.activa:
            return False
        if self.fecha_vigencia and self.fecha_vigencia > hoy:
            return False
        if self.fecha_fin_vigencia and self.fecha_fin_vigencia < hoy:
            return False
        return True


class RequisitoLegal(models.Model):

    class Categoria(models.TextChoices):
        PREVENCION = 'prevencion', 'Prevención de riesgos'
        FORMACION = 'formacion', 'Formación y capacitación'
        VIGILANCIA = 'vigilancia', 'Vigilancia de la salud'
        EPIS = 'epis', 'EPIs y seguridad'
        INSTALACIONES = 'instalaciones', 'Instalaciones y equipos'
        EMERGENCIAS = 'emergencias', 'Emergencias y evacuación'
        DOCUMENTACION = 'documentacion', 'Documentación'
        NOTIFICACION = 'notificacion', 'Notificación a autoridades'
        OTROS = 'otros', 'Otros requisitos'

    normativa = models.ForeignKey(
        NormativaLegal,
        on_delete=models.CASCADE,
        related_name='requisitos',
        verbose_name='normativa',
    )
    titulo = models.CharField('título del requisito', max_length=300)
    descripcion = models.TextField('descripción / obligación legal')
    categoria = models.CharField(
        'categoría',
        max_length=30,
        choices=Categoria.choices,
        default=Categoria.PREVENCION,
    )
    articulo = models.CharField(
        'artículo / apartado',
        max_length=100,
        blank=True,
        default='',
    )
    plazo_cumplimiento = models.CharField(
        'plazo de cumplimiento',
        max_length=200,
        blank=True,
        default='',
        help_text='ej: Permanente, 6 meses, A partir de la publicación',
    )
    observaciones = models.TextField('observaciones', blank=True, default='')

    created_at = models.DateTimeField('creado el', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado el', auto_now=True)

    class Meta:
        verbose_name = 'requisito legal'
        verbose_name_plural = 'requisitos legales'
        ordering = ['normativa', 'articulo', 'titulo']
        indexes = [
            models.Index(fields=['normativa', 'categoria']),
            models.Index(fields=['categoria']),
        ]

    def __str__(self):
        return f'{self.normativa} — {self.titulo[:70]}'

    @property
    def badge_categoria(self):
        return {
            'prevencion': 'badge-danger',
            'formacion': 'badge-info',
            'vigilancia': 'badge-warning',
            'epis': 'badge-primary',
            'instalaciones': 'badge-secondary',
            'emergencias': 'badge-moderate',
            'documentacion': 'badge-info',
            'notificacion': 'badge-warning',
            'otros': 'badge-secondary',
        }.get(self.categoria, 'badge-secondary')


class CumplimientoLegal(models.Model):

    class Estado(models.TextChoices):
        CUMPLE = 'cumple', 'Cumple'
        NO_CUMPLE = 'no_cumple', 'No cumple'
        EN_CURSO = 'en_curso', 'En curso de cumplimiento'
        NO_APLICA = 'no_aplica', 'No aplica'
        PENDIENTE = 'pendiente', 'Pendiente de evaluación'

    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='cumplimientos_legales',
        verbose_name='empresa',
    )
    requisito = models.ForeignKey(
        RequisitoLegal,
        on_delete=models.CASCADE,
        related_name='cumplimientos',
        verbose_name='requisito legal',
    )
    estado = models.CharField(
        'estado de cumplimiento',
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    evaluado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cumplimientos_evaluados',
        verbose_name='evaluado por',
    )
    fecha_evaluacion = models.DateField('fecha de evaluación', null=True, blank=True)
    fecha_proxima_revision = models.DateField('próxima revisión', null=True, blank=True)
    evidencia = models.TextField(
        'evidencia de cumplimiento',
        blank=True,
        default='',
        help_text='Documentos, registros, acciones que acreditan el cumplimiento',
    )
    acciones_necesarias = models.TextField(
        'acciones necesarias para cumplir',
        blank=True,
        default='',
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cumplimientos_responsable',
        verbose_name='responsable',
    )
    nc_generada = models.ForeignKey(
        'corrective_actions.NoConformidad',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cumplimiento_legal',
        verbose_name='NC generada',
    )
    notas = models.TextField('notas', blank=True, default='')

    created_at = models.DateTimeField('creado el', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado el', auto_now=True)

    class Meta:
        verbose_name = 'cumplimiento legal'
        verbose_name_plural = 'cumplimientos legales'
        ordering = ['empresa', 'requisito']
        unique_together = ('empresa', 'requisito')
        indexes = [
            models.Index(fields=['empresa', 'estado']),
            models.Index(fields=['empresa', 'fecha_proxima_revision']),
        ]

    def __str__(self):
        return f'{self.empresa} — {self.requisito} → {self.get_estado_display()}'

    @property
    def badge_estado(self):
        return {
            'cumple': 'badge-success',
            'no_cumple': 'badge-danger',
            'en_curso': 'badge-warning',
            'no_aplica': 'badge-secondary',
            'pendiente': 'badge-moderate',
        }.get(self.estado, 'badge-secondary')

    @property
    def dias_para_revision(self):
        from datetime import date
        if not self.fecha_proxima_revision:
            return None
        delta = self.fecha_proxima_revision - date.today()
        return delta.days

    @property
    def revision_vencida(self):
        from datetime import date
        if not self.fecha_proxima_revision:
            return False
        return self.fecha_proxima_revision < date.today()

    @property
    def revision_proxima(self):
        from datetime import date
        if not self.fecha_proxima_revision:
            return False
        hoy = date.today()
        delta = (self.fecha_proxima_revision - hoy).days
        return 0 <= delta <= 30


class AlertaLegal(models.Model):

    class Tipo(models.TextChoices):
        VENCIMIENTO = 'vencimiento', 'Vencimiento de revisión'
        CAMBIO_NORMATIVO = 'cambio_normativo', 'Cambio normativo'
        NO_CUMPLIMIENTO = 'no_cumplimiento', 'No cumplimiento detectado'
        RECORDATORIO = 'recordatorio', 'Recordatorio'

    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='alertas_legales',
        verbose_name='empresa',
    )
    tipo = models.CharField('tipo de alerta', max_length=30, choices=Tipo.choices)
    titulo = models.CharField('título', max_length=255)
    descripcion = models.TextField('descripción')
    cumplimiento = models.ForeignKey(
        CumplimientoLegal,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='alertas',
        verbose_name='cumplimiento relacionado',
    )
    normativa = models.ForeignKey(
        NormativaLegal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alertas',
        verbose_name='normativa relacionada',
    )
    leida = models.BooleanField('leída', default=False)
    resuelta = models.BooleanField('resuelta', default=False)
    fecha_creacion = models.DateTimeField('fecha de creación', auto_now_add=True)

    class Meta:
        verbose_name = 'alerta legal'
        verbose_name_plural = 'alertas legales'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['empresa', 'leida']),
            models.Index(fields=['empresa', 'resuelta']),
        ]

    def __str__(self):
        return f'{self.get_tipo_display()}: {self.titulo}'

    @property
    def badge_tipo(self):
        return {
            'vencimiento': 'badge-danger',
            'cambio_normativo': 'badge-warning',
            'no_cumplimiento': 'badge-danger',
            'recordatorio': 'badge-info',
        }.get(self.tipo, 'badge-secondary')
