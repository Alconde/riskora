from django.conf import settings
from django.db import models
from apps.core.mixins import AuditFieldsMixin


class CausaAccidente(AuditFieldsMixin, models.Model):

    class Categoria(models.TextChoices):
        INMEDIATA = 'inmediata', 'Causa inmediata'
        BASICA = 'basica', 'Causa basica'
        ORGANIZATIVA = 'organizativa', 'Causa organizativa'

    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='causas_accidente',
        verbose_name='empresa',
    )
    nombre = models.CharField(max_length=200, verbose_name='nombre')
    categoria = models.CharField(
        max_length=20,
        choices=Categoria.choices,
        default=Categoria.INMEDIATA,
        verbose_name='categoria',
    )
    activa = models.BooleanField(default=True, verbose_name='activa')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'causa de accidente'
        verbose_name_plural = 'causas de accidente'
        ordering = ['categoria', 'nombre']

    def __str__(self):
        return self.nombre


class Accidente(AuditFieldsMixin, models.Model):

    class Tipo(models.TextChoices):
        TRABAJO = 'trabajo', 'Accidente de trabajo'
        ITINERE = 'itinere', 'Accidente in itinere'

    class Gravedad(models.TextChoices):
        SIN_BAJA = 'sin_baja', 'Sin baja'
        BAJA_TEMPORAL = 'baja_temporal', 'Baja temporal'
        BAJA_PERMANENTE = 'baja_permanente', 'Baja permanente'
        MORTAL = 'mortal', 'Mortal'

    class TipoLesion(models.TextChoices):
        CORTES = 'cortes', 'Cortes'
        FRACTURAS = 'fracturas', 'Fracturas'
        CONTUSIONES = 'contusiones', 'Contusiones'
        QUEMADURAS = 'quemaduras', 'Quemaduras'
        INTOXICACION = 'intoxicacion', 'Intoxicacion'
        ATRAPAMIENTO = 'atrapamiento', 'Atrapamiento'
        CAIDA = 'caida', 'Caida'
        OTRO = 'otro', 'Otro'

    class Estado(models.TextChoices):
        ABIERTO = 'abierto', 'Abierto'
        EN_INVESTIGACION = 'en_investigacion', 'En investigacion'
        CERRADO = 'cerrado', 'Cerrado'

    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='accidentes',
        verbose_name='empresa',
    )
    codigo = models.CharField(max_length=30, unique=True, verbose_name='codigo')
    titulo = models.CharField(max_length=200, verbose_name='titulo')
    fecha = models.DateTimeField(verbose_name='fecha y hora del accidente')
    centro_trabajo = models.ForeignKey(
        'workcenters.WorkCenter',
        on_delete=models.CASCADE,
        related_name='accidentes',
        verbose_name='centro de trabajo',
    )
    ubicacion = models.CharField(
        max_length=200, blank=True, verbose_name='ubicacion especifica'
    )
    tipo = models.CharField(
        max_length=20,
        choices=Tipo.choices,
        default=Tipo.TRABAJO,
        verbose_name='tipo de accidente',
    )
    gravedad = models.CharField(
        max_length=20,
        choices=Gravedad.choices,
        default=Gravedad.SIN_BAJA,
        verbose_name='gravedad',
    )
    tipo_lesion = models.CharField(
        max_length=20,
        choices=TipoLesion.choices,
        default=TipoLesion.OTRO,
        verbose_name='tipo de lesion',
    )
    parte_cuerpo = models.CharField(
        max_length=200, blank=True, verbose_name='parte del cuerpo afectada'
    )
    descripcion = models.TextField(verbose_name='descripcion del accidente')
    testigos = models.TextField(blank=True, verbose_name='testigos')
    trabajador_afectado = models.ForeignKey(
        'workers.Worker',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accidentes',
        verbose_name='trabajador afectado',
    )
    notify_salud = models.BooleanField(
        default=False, verbose_name='notificado a vigilancia de la salud'
    )
    notify_inspeccion = models.BooleanField(
        default=False, verbose_name='notificado a inspeccion de trabajo'
    )
    fecha_notificacion = models.DateField(
        null=True, blank=True, verbose_name='fecha de notificacion'
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ABIERTO,
        verbose_name='estado',
    )
    causas = models.ManyToManyField(
        CausaAccidente,
        blank=True,
        related_name='accidentes',
        verbose_name='causas identificadas',
    )
    nc_generada = models.ForeignKey(
        'corrective_actions.NoConformidad',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accidentes',
        verbose_name='NC generada',
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='accidentes_creados',
        verbose_name='creado por',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'accidente'
        verbose_name_plural = 'accidentes'
        ordering = ['-fecha', '-created_at']
        indexes = [
            models.Index(fields=['empresa', 'estado']),
            models.Index(fields=['empresa', 'centro_trabajo']),
            models.Index(fields=['fecha']),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.titulo}'

    @property
    def badge_estado(self):
        mapping = {
            'abierto': 'badge-danger',
            'en_investigacion': 'badge-warning',
            'cerrado': 'badge-success',
        }
        return mapping.get(self.estado, 'badge-secondary')

    @property
    def badge_gravedad(self):
        mapping = {
            'sin_baja': 'badge-secondary',
            'baja_temporal': 'badge-warning',
            'baja_permanente': 'badge-danger',
            'mortal': 'badge-danger',
        }
        return mapping.get(self.gravedad, 'badge-secondary')

    @property
    def tiene_investigacion(self):
        return hasattr(self, 'investigacion') and self.investigacion is not None


class InvestigacionAccidente(AuditFieldsMixin, models.Model):

    RIESGO_CHOICES = [
        ('', '--- Seleccionar ---'),
        ('caidas_mismo_nivel', 'Caídas al mismo nivel'),
        ('caidas_distinto_nivel', 'Caídas a distinto nivel'),
        ('caida_objetos', 'Caída de objetos'),
        ('proyeccion_fragmentos', 'Proyección de fragmentos y/o partículas'),
        ('atrapamientos', 'Atrapamientos'),
        ('golpes', 'Golpes contra objetos'),
        ('cortes', 'Cortes y cortaduras'),
        ('quemaduras', 'Quemaduras'),
        ('electrocucion', 'Electrocución'),
        ('explosion', 'Explosión'),
        ('incendio', 'Incendio'),
        ('intoxicacion', 'Intoxicación'),
        ('asfixia', 'Asfixia'),
        ('ahogamiento', 'Ahogamiento'),
        ('sordera', 'Pérdida auditiva'),
        ('lesiones_osteomusculares', 'Lesiones osteomusculares'),
        ('enfermedad_profesional', 'Enfermedad profesional'),
        ('ergonomico', 'Riesgo ergonómico'),
        ('psicosocial', 'Riesgo psicosocial'),
        ('biologico', 'Riesgo biológico'),
        ('radiacion', 'Exposición a radiaciones'),
        ('derrame_sustancias', 'Derrame de sustancias'),
        ('otro', 'Otro'),
    ]

    class Metodologia(models.TextChoices):
        CINCO_PORQUES = '_5_porques', '5 Porques'
        ISHIKAWA = 'ishikawa', 'Ishikawa (Espina de pez)'
        ARBOL_CAUSAS = 'arbol_causas', 'Arbol de causas'
        OTRO = 'otro', 'Otro'

    class Estado(models.TextChoices):
        EN_CURSO = 'en_curso', 'En curso'
        COMPLETADA = 'completada', 'Completada'

    accidente = models.OneToOneField(
        Accidente,
        on_delete=models.CASCADE,
        related_name='investigacion',
        verbose_name='accidente',
    )
    fecha_inicio = models.DateField(verbose_name='fecha de inicio')
    metodologia = models.CharField(
        max_length=20,
        choices=Metodologia.choices,
        default=Metodologia.CINCO_PORQUES,
        verbose_name='metodologia de analisis',
    )
    puesto_trabajo = models.CharField(
        max_length=200, blank=True, verbose_name='puesto de trabajo'
    )
    horas_trabajador = models.PositiveIntegerField(
        null=True, blank=True, verbose_name='horas trabajadas (1-8)'
    )
    hora_dia = models.TimeField(
        null=True, blank=True, verbose_name='hora del dia'
    )
    edad = models.PositiveIntegerField(
        null=True, blank=True, verbose_name='edad del trabajador'
    )
    tiempo_puesto = models.CharField(
        max_length=100, blank=True, verbose_name='tiempo en el puesto de trabajo'
    )
    acto_condicion_detectada = models.TextField(
        blank=True, verbose_name='acto o condicion detectada'
    )
    riesgo_identificado = models.CharField(
        max_length=40,
        choices=RIESGO_CHOICES,
        blank=True,
        verbose_name='riesgo identificado',
    )
    medidas_preventivas = models.TextField(
        blank=True, verbose_name='medidas preventivas propuestas'
    )
    plazo = models.DateField(
        null=True, blank=True, verbose_name='plazo de implantacion'
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='investigaciones_responsable',
        verbose_name='responsable de medidas',
    )
    coste = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name='coste estimado'
    )
    riesgo_en_er = models.BooleanField(
        default=False, verbose_name='riesgo en evaluacion de riesgos'
    )
    descripcion_ideal = models.TextField(
        blank=True, verbose_name='descripcion de lo que deberia haber pasado'
    )
    descripcion_real = models.TextField(
        blank=True, verbose_name='descripcion de lo que realmente paso'
    )
    causas_inmediatas = models.TextField(
        blank=True, verbose_name='causas inmediatas'
    )
    causas_basicas = models.TextField(
        blank=True, verbose_name='causas basicas'
    )
    causas_organizativas = models.TextField(
        blank=True, verbose_name='causas organizativas'
    )
    conclusiones = models.TextField(blank=True, verbose_name='conclusiones')
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.EN_CURSO,
        verbose_name='estado',
    )
    investigador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='investigaciones_accidente',
        verbose_name='investigador',
    )
    revisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='investigaciones_revisadas',
        verbose_name='revisor',
    )
    fecha_firma = models.DateField(
        null=True, blank=True, verbose_name='fecha de firma'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'investigacion de accidente'
        verbose_name_plural = 'investigaciones de accidente'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f'Investigacion: {self.accidente.codigo}'

    @property
    def badge_estado(self):
        mapping = {
            'en_curso': 'badge-warning',
            'completada': 'badge-success',
        }
        return mapping.get(self.estado, 'badge-secondary')


class ProcedimientoInvestigacion(AuditFieldsMixin, models.Model):
    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='procedimientos_investigacion',
        verbose_name='empresa',
    )
    titulo = models.CharField(max_length=200, verbose_name='titulo')
    descripcion = models.TextField(blank=True, verbose_name='descripcion')
    archivo = models.FileField(
        upload_to='incidentes/procedimientos/',
        verbose_name='archivo del procedimiento',
    )
    version = models.CharField(max_length=20, default='1.0', verbose_name='version')
    activo = models.BooleanField(default=True, verbose_name='activo')
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='procedimientos_investigacion',
        verbose_name='subido por',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'procedimiento de investigacion'
        verbose_name_plural = 'procedimientos de investigacion'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.titulo} v{self.version}'


class Incidente(AuditFieldsMixin, models.Model):

    class GravedadPotencial(models.TextChoices):
        LEVE = 'leve', 'Leve'
        MODERADA = 'moderada', 'Moderada'
        GRAVE = 'grave', 'Grave'
        MUY_GRAVE = 'muy_grave', 'Muy grave'

    class Estado(models.TextChoices):
        ABIERTO = 'abierto', 'Abierto'
        EN_ESTUDIO = 'en_estudio', 'En estudio'
        CERRADO = 'cerrado', 'Cerrado'

    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='incidentes',
        verbose_name='empresa',
    )
    codigo = models.CharField(max_length=30, unique=True, verbose_name='codigo')
    titulo = models.CharField(max_length=200, verbose_name='titulo')
    fecha = models.DateTimeField(verbose_name='fecha y hora del incidente')
    centro_trabajo = models.ForeignKey(
        'workcenters.WorkCenter',
        on_delete=models.CASCADE,
        related_name='incidentes',
        verbose_name='centro de trabajo',
    )
    ubicacion = models.CharField(
        max_length=200, blank=True, verbose_name='ubicacion especifica'
    )
    descripcion = models.TextField(verbose_name='que ocurrio')
    potencial_dano = models.TextField(
        blank=True, verbose_name='que dano podria haber causado'
    )
    testigos = models.TextField(blank=True, verbose_name='testigos')
    trabajador_reports = models.ForeignKey(
        'workers.Worker',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidentes_reportados',
        verbose_name='trabajador que reporto',
    )
    gravedad_potencial = models.CharField(
        max_length=20,
        choices=GravedadPotencial.choices,
        default=GravedadPotencial.LEVE,
        verbose_name='gravedad potencial',
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ABIERTO,
        verbose_name='estado',
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='incidentes_creados',
        verbose_name='creado por',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'incidente'
        verbose_name_plural = 'incidentes'
        ordering = ['-fecha', '-created_at']
        indexes = [
            models.Index(fields=['empresa', 'estado']),
            models.Index(fields=['empresa', 'centro_trabajo']),
            models.Index(fields=['fecha']),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.titulo}'

    @property
    def badge_estado(self):
        mapping = {
            'abierto': 'badge-danger',
            'en_estudio': 'badge-warning',
            'cerrado': 'badge-success',
        }
        return mapping.get(self.estado, 'badge-secondary')

    @property
    def badge_gravedad_potencial(self):
        mapping = {
            'leve': 'badge-secondary',
            'moderada': 'badge-warning',
            'grave': 'badge-danger',
            'muy_grave': 'badge-danger',
        }
        return mapping.get(self.gravedad_potencial, 'badge-secondary')
