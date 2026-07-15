from django.conf import settings
from django.db import models
from apps.core.mixins import AuditFieldsMixin


class EnfermedadProfesional(AuditFieldsMixin, models.Model):

    class AgenteCausante(models.TextChoices):
        QUIMICO = 'quimico', 'Quimico'
        BIOLOGICO = 'biologico', 'Biologico'
        FISICO = 'fisico', 'Fisico'
        ERGONOMICO = 'ergonomico', 'Ergonomico'
        PSICOSOCIAL = 'psicosocial', 'Psicosocial'
        MIXTO = 'mixto', 'Mixto'
        OTRO = 'otro', 'Otro'

    class Gravedad(models.TextChoices):
        LEVE = 'leve', 'Leve'
        MODERADA = 'moderada', 'Moderada'
        GRAVE = 'grave', 'Grave'
        MUY_GRAVE = 'muy_grave', 'Muy grave'

    class Estado(models.TextChoices):
        ABIERTO = 'abierto', 'Abierto'
        EN_INVESTIGACION = 'en_investigacion', 'En investigacion'
        CERRADO = 'cerrado', 'Cerrado'

    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='enfermedades_profesionales',
        verbose_name='empresa',
    )
    codigo = models.CharField(max_length=30, unique=True, verbose_name='codigo')
    titulo = models.CharField(max_length=200, verbose_name='titulo')
    fecha_diagnostico = models.DateField(verbose_name='fecha de diagnostico')
    centro_trabajo = models.ForeignKey(
        'workcenters.WorkCenter',
        on_delete=models.CASCADE,
        related_name='enfermedades_profesionales',
        verbose_name='centro de trabajo',
    )
    trabajador_afectado = models.ForeignKey(
        'workers.Worker',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enfermedades_profesionales',
        verbose_name='trabajador afectado',
    )
    nombre_enfermedad = models.CharField(
        max_length=300, verbose_name='nombre de la enfermedad'
    )
    agente_causante = models.CharField(
        max_length=20,
        choices=AgenteCausante.choices,
        default=AgenteCausante.OTRO,
        verbose_name='agente causante',
    )
    tipo_exposicion = models.CharField(
        max_length=300, blank=True, verbose_name='tipo de exposicion'
    )
    duracion_exposicion = models.CharField(
        max_length=100, blank=True, verbose_name='duracion de la exposicion'
    )
    parte_cuerpo = models.CharField(
        max_length=200, blank=True, verbose_name='parte del cuerpo afectada'
    )
    gravedad = models.CharField(
        max_length=20,
        choices=Gravedad.choices,
        default=Gravedad.LEVE,
        verbose_name='gravedad',
    )
    descripcion = models.TextField(verbose_name='descripcion de la enfermedad')
    testigos = models.TextField(blank=True, verbose_name='testigos')
    notify_salud = models.BooleanField(
        default=False, verbose_name='notificado a vigilancia de la salud'
    )
    notify_inspeccion = models.BooleanField(
        default=False, verbose_name='notificado a inspeccion de trabajo'
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
        related_name='enfermedades_profesionales_creadas',
        verbose_name='creado por',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'enfermedad profesional'
        verbose_name_plural = 'enfermedades profesionales'
        ordering = ['-fecha_diagnostico', '-created_at']
        indexes = [
            models.Index(fields=['empresa', 'estado']),
            models.Index(fields=['empresa', 'centro_trabajo']),
            models.Index(fields=['fecha_diagnostico']),
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
            'leve': 'badge-secondary',
            'moderada': 'badge-warning',
            'grave': 'badge-danger',
            'muy_grave': 'badge-danger',
        }
        return mapping.get(self.gravedad, 'badge-secondary')

    @property
    def tiene_investigacion(self):
        return hasattr(self, 'investigacion') and self.investigacion is not None


class InvestigacionEEPP(AuditFieldsMixin, models.Model):

    RIESGO_CHOICES = [
        ('', '--- Seleccionar ---'),
        ('sordera', 'Pérdida auditiva (sordera)'),
        ('vibracion_manos', 'Síndrome del brazo por vibración'),
        ('lesiones_osteomusculares', 'Lesiones osteomusculares (TME)'),
        ('dermatitis', 'Dermatitis de contacto'),
        ('asma_laboral', 'Asma laboral'),
        ('cancer', 'Cancer profesional'),
        ('intoxicacion_cronica', 'Intoxicacion cronica'),
        ('silicosis', 'Silicosis'),
        ('asbestosis', 'Asbestosis (amianto)'),
        ('sordera_ruido', 'Hipoacusia por ruido'),
        ('tendinitis', 'Tendinitis'),
        ('hernia_discal', 'Hernia discal lumbar'),
        ('stress_laboral', 'Stress laboral'),
        ('burnout', 'Burnout'),
        ('agresion_psicologica', 'Agresion psicologica'),
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

    enfermedad = models.OneToOneField(
        EnfermedadProfesional,
        on_delete=models.CASCADE,
        related_name='investigacion',
        verbose_name='enfermedad profesional',
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
        related_name='investigaciones_epp_responsable',
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
        related_name='investigaciones_eepp',
        verbose_name='investigador',
    )
    revisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='investigaciones_eepp_revisadas',
        verbose_name='revisor',
    )
    fecha_firma = models.DateField(
        null=True, blank=True, verbose_name='fecha de firma'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'investigacion de enfermedad profesional'
        verbose_name_plural = 'investigaciones de enfermedades profesionales'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f'Investigacion EEPP: {self.enfermedad.codigo}'

    @property
    def badge_estado(self):
        mapping = {
            'en_curso': 'badge-warning',
            'completada': 'badge-success',
        }
        return mapping.get(self.estado, 'badge-secondary')


class ProcedimientoInvestigacionEEPP(AuditFieldsMixin, models.Model):
    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='procedimientos_investigacion_eepp',
        verbose_name='empresa',
    )
    titulo = models.CharField(max_length=200, verbose_name='titulo')
    descripcion = models.TextField(blank=True, verbose_name='descripcion')
    archivo = models.FileField(
        upload_to='eepp/procedimientos/',
        verbose_name='archivo del procedimiento',
    )
    version = models.CharField(max_length=20, default='1.0', verbose_name='version')
    activo = models.BooleanField(default=True, verbose_name='activo')
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='procedimientos_investigacion_eepp',
        verbose_name='subido por',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'procedimiento de investigacion EEPP'
        verbose_name_plural = 'procedimientos de investigacion EEPP'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.titulo} v{self.version}'
