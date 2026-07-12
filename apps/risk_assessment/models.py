from django.conf import settings
from django.db import models


class TipoPeligro(models.Model):
    """
    Catálogo maestro de tipos de peligro.
    Basado en el Anexo I del RD 39/1997 y guías INSST.
    """
    CATEGORIA_CHOICES = [
        ('mecanico', 'Mecánico'),
        ('quimico', 'Químico'),
        ('electrico', 'Eléctrico'),
        ('ergonomico', 'Ergonómico'),
        ('psicosocial', 'Psicosocial'),
        ('biologico', 'Biológico'),
        ('fisico', 'Físico'),
        ('locativo', 'Locativo (caídas, golpes)'),
        ('incendio', 'Incendio y explosión'),
        ('otro', 'Otro'),
    ]

    nombre = models.CharField('nombre del peligro', max_length=200)
    codigo = models.CharField('código', max_length=50, unique=True)
    categoria = models.CharField(
        'categoría',
        max_length=30,
        choices=CATEGORIA_CHOICES,
    )
    referencia_normativa = models.CharField(
        'referencia normativa',
        max_length=300,
        blank=True,
        help_text='Ej: RD 1215/1997, RD 374/2001, Ley 31/1995',
    )
    descripcion = models.TextField('descripción', blank=True)
    activo = models.BooleanField('activo', default=True)

    created_at = models.DateTimeField('creado el', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado el', auto_now=True)

    class Meta:
        verbose_name = 'tipo de peligro'
        verbose_name_plural = 'tipos de peligro'
        ordering = ['categoria', 'nombre']

    def __str__(self):
        return f'{self.nombre} ({self.get_categoria_display()})'


class EvaluacionRiesgos(models.Model):
    """
    Evaluación de Riesgos - Documento maestro de evaluación.
    Metodología INSST: Matriz de Probabilidad × Severidad.

    Referencia: Art. 16 Ley 31/1995, RD 39/1997 Art. 17-20,
    Guía Técnica del INSST para la evaluación de riesgos.
    """

    class Estado(models.TextChoices):
        BORRADOR = 'borrador', 'Borrador'
        PENDIENTE_APROBACION = 'pendiente_aprobacion', 'Pendiente de aprobación'
        APROBADA = 'aprobada', 'Aprobada'
        EN_REVISION = 'en_revision', 'En revisión'
        EXPIRADA = 'expirada', 'Expirada'

    class MetodoEvaluacion(models.TextChoices):
        PROPIO = 'propio', 'Riesgo propio'
        COMUN = 'comun', 'Riesgo común'
        ESPECIFICO = 'especifico', 'Específico del sector'

    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='evaluaciones_riesgos',
        verbose_name='empresa',
    )
    centro_trabajo = models.ForeignKey(
        'workcenters.WorkCenter',
        on_delete=models.CASCADE,
        related_name='evaluaciones_riesgos',
        verbose_name='centro de trabajo',
    )

    titulo = models.CharField('título de la evaluación', max_length=255)
    fecha_evaluacion = models.DateField('fecha de evaluación')
    fecha_proxima_revision = models.DateField(
        'fecha de próxima revisión',
        help_text='Art. 16 Ley 31/1995: revisiones periódicas obligatorias',
    )
    metodologia = models.CharField(
        'método de evaluación',
        max_length=20,
        choices=MetodoEvaluacion.choices,
        default=MetodoEvaluacion.PROPIO,
    )

    revisado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='evaluaciones_revisadas',
        verbose_name='revisado por',
    )
    aprobado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evaluaciones_aprobadas',
        verbose_name='aprobado por',
    )
    fecha_aprobacion = models.DateField('fecha de aprobación', null=True, blank=True)

    estado = models.CharField(
        'estado',
        max_length=25,
        choices=Estado.choices,
        default=Estado.BORRADOR,
    )
    version = models.CharField('versión', max_length=20, default='1.0')
    observaciones = models.TextField('observaciones', blank=True)

    created_at = models.DateTimeField('creado el', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado el', auto_now=True)

    class Meta:
        verbose_name = 'evaluación de riesgos'
        verbose_name_plural = 'evaluaciones de riesgos'
        ordering = ['-fecha_evaluacion', '-created_at']

    def __str__(self):
        return f'{self.titulo} ({self.get_estado_display()})'

    @property
    def total_items(self):
        return self.items.count()

    @property
    def items_requieren_accion(self):
        return self.items.filter(nivel_riesgo__in=['moderado', 'importante', 'intolerable']).count()


class ItemEvaluacionRiesgos(models.Model):
    """
    Cada fila de la matriz de evaluación de riesgos.
    Un item = puesto de trabajo + peligro + evaluación INSST.

    Cálculo: Grado de Riesgo = Probabilidad × Severidad
    """

    class Probabilidad(models.IntegerChoices):
        BAJA = 1, 'Baja'
        MEDIA = 2, 'Media'
        ALTA = 3, 'Alta'

    class Severidad(models.IntegerChoices):
        LIGERAMENTE_DANINO = 1, 'Ligeramente dañino'
        DANINO = 2, 'Dañino'
        EXTREMADAMENTE_DANINO = 3, 'Extremadamente dañino'

    class NivelRiesgo(models.TextChoices):
        TRIVIAL = 'trivial', 'Trivial'
        TOLERABLE = 'tolerable', 'Tolerable'
        MODERADO = 'moderado', 'Moderado'
        IMPORTANTE = 'importante', 'Importante'
        INTOLERABLE = 'intolerable', 'Intolerable'

    evaluacion = models.ForeignKey(
        EvaluacionRiesgos,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='evaluación',
    )
    puesto_trabajo = models.ForeignKey(
        'workers.JobPosition',
        on_delete=models.CASCADE,
        related_name='items_evaluacion',
        verbose_name='puesto de trabajo',
    )
    tipo_peligro = models.ForeignKey(
        TipoPeligro,
        on_delete=models.PROTECT,
        related_name='items_evaluacion',
        verbose_name='tipo de peligro',
    )

    descripcion_peligro = models.TextField(
        'descripción del peligro',
        help_text='Descripción detallada del peligro identificado',
    )
    medidas_existentes = models.TextField(
        'medidas preventivas existentes',
        help_text='Medidas de protección y prevención actualmente implementadas',
    )

    probabilidad = models.PositiveSmallIntegerField(
        'probabilidad',
        choices=Probabilidad.choices,
        help_text='1=Baja, 2=Media, 3=Alta',
    )
    severidad = models.PositiveSmallIntegerField(
        'severidad (consecuencias)',
        choices=Severidad.choices,
        help_text='1=Ligeramente dañino, 2=Dañino, 3=Extremadamente dañino',
    )

    grado_riesgo = models.PositiveSmallIntegerField(
        'grado de riesgo',
        editable=False,
        help_text='Calculado automáticamente: Probabilidad × Severidad (escala 1-5)',
    )
    nivel_riesgo = models.CharField(
        'nivel de riesgo',
        max_length=20,
        choices=NivelRiesgo.choices,
        editable=False,
    )

    medidas_propuestas = models.TextField(
        'nuevas medidas preventivas propuestas',
        blank=True,
        help_text='Medidas a implementar para reducir el riesgo',
    )
    responsable_medida = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='medidas_asignadas',
        verbose_name='responsable de la medida',
    )
    fecha_limite_implementacion = models.DateField(
        'fecha límite de implementación',
        null=True,
        blank=True,
    )
    estado_implementacion = models.CharField(
        'estado de implementación',
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('en_curso', 'En curso'),
            ('implementada', 'Implementada'),
            ('verificada', 'Verificada'),
        ],
        default='pendiente',
    )

    created_at = models.DateTimeField('creado el', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado el', auto_now=True)

    class Meta:
        verbose_name = 'item de evaluación de riesgos'
        verbose_name_plural = 'items de evaluación de riesgos'
        ordering = ['evaluacion', 'puesto_trabajo', 'tipo_peligro']

    def __str__(self):
        return (
            f'{self.puesto_trabajo} - {self.tipo_peligro} '
            f'[GR={self.grado_riesgo}]'
        )

    @property
    def probabilidad_display(self):
        return self.get_probabilidad_display()

    @property
    def severidad_display(self):
        return self.get_severidad_display()

    @property
    def requiere_accion(self):
        return self.nivel_riesgo in ('moderado', 'importante', 'intolerable')


class NivelRiesgoReferencia(models.Model):
    """
    Tabla de referencia de los 9 niveles de riesgo de la matriz INSST.
    Permite configurar colores y etiquetas desde el admin.
    Probabilidad (1-3) × Severidad (1-3) = GR (1-5)
    """

    grado = models.PositiveSmallIntegerField(
        'grado de riesgo (GR)',
        unique=True,
        help_text='Valor de 1 a 5 según la matriz INSST',
    )
    probabilidad = models.PositiveSmallIntegerField('probabilidad')
    severidad = models.PositiveSmallIntegerField('severidad')
    nivel = models.CharField('nivel', max_length=20)
    etiqueta = models.CharField('etiqueta', max_length=50)
    color = models.CharField('color hex', max_length=7, default='#000000')
    color_fondo = models.CharField('color de fondo', max_length=7, default='#ffffff')
    color_texto = models.CharField('color de texto', max_length=7, default='#000000')
    descripcion = models.TextField('descripción', blank=True)

    class Meta:
        verbose_name = 'nivel de riesgo de referencia'
        verbose_name_plural = 'niveles de riesgo de referencia'
        ordering = ['grado']

    def __str__(self):
        return f'GR {self.grado} - {self.etiqueta}'
