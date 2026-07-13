from django.conf import settings
from django.db import models


class ItemPlanificacion(models.Model):

    class TipoFactorRiesgo(models.TextChoices):
        EVITABLES = 'evitables', 'Evitables'
        MONITORIZABLES = 'monitorizables', 'Monitorizables'
        NO_EVITABLES = 'no_evitables', 'No evitables'

    RIESGO_CHOICES = [
        ('', '--- Seleccionar ---'),
        ('contactos_electricos', 'Contactos electricos'),
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
        ('riesgos_profesionales', 'Riesgos no incluido en las listas sobre enfermedades profesionales'),
        ('otro', 'Otro'),
    ]

    class PBChoices(models.TextChoices):
        BAJA = 'B', 'Baja'
        MEDIA = 'M', 'Media'
        ALTA = 'A', 'Alta'
        NV = 'NV', 'No valorada'

    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        EN_CURSO = 'en_curso', 'En curso'
        IMPLEMENTADA = 'implementada', 'Implementada'
        VERIFICADA = 'verificada', 'Verificada'
        CONTINUA = 'continua', 'Continua'

    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='items_planificacion',
        verbose_name='empresa',
    )
    evaluacion_riesgos = models.ForeignKey(
        'risk_assessment.EvaluacionRiesgos',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items_planificacion',
        verbose_name='evaluacion de riesgos',
    )
    ambito_puesto = models.CharField(
        max_length=300, blank=True, verbose_name='ambito / puesto de trabajo'
    )
    tipo_factor_riesgo = models.CharField(
        max_length=20,
        choices=TipoFactorRiesgo.choices,
        default=TipoFactorRiesgo.EVITABLES,
        verbose_name='tipo de factor de riesgo',
    )
    factor_riesgo = models.TextField(verbose_name='factor de riesgo')
    detalle = models.TextField(blank=True, verbose_name='detalle')
    riesgos = models.CharField(
        max_length=60,
        choices=RIESGO_CHOICES,
        blank=True,
        verbose_name='riesgos',
    )
    pb = models.CharField(
        max_length=2,
        choices=PBChoices.choices,
        default=PBChoices.NV,
        verbose_name='probabilidad (PB)',
    )
    sv = models.CharField(
        max_length=2,
        choices=PBChoices.choices,
        default=PBChoices.NV,
        verbose_name='severidad (SV)',
    )
    gr = models.CharField(
        max_length=2,
        choices=PBChoices.choices,
        default=PBChoices.NV,
        verbose_name='grado de riesgo (GR)',
    )
    medidas_preventivas = models.TextField(
        blank=True, verbose_name='medidas preventivas'
    )
    detalle_medida = models.TextField(
        blank=True, verbose_name='detalle de la medida / accion correctora'
    )
    plazo_limite = models.CharField(
        max_length=100, blank=True, verbose_name='plazo limite'
    )
    fecha_objetivo = models.DateField(
        null=True, blank=True, verbose_name='fecha objetivo'
    )
    responsable = models.CharField(
        max_length=200, blank=True, verbose_name='responsable'
    )
    costes = models.CharField(
        max_length=100, blank=True, verbose_name='costes'
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        verbose_name='estado',
    )
    origen = models.CharField(
        max_length=200, blank=True, verbose_name='origen'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'item de planificacion preventiva'
        verbose_name_plural = 'items de planificacion preventiva'
        ordering = ['tipo_factor_riesgo', 'factor_riesgo']
        indexes = [
            models.Index(fields=['empresa', 'estado']),
            models.Index(fields=['empresa', 'tipo_factor_riesgo']),
        ]

    def __str__(self):
        return f'{self.ambito_puesto} - {self.factor_riesgo[:60]}'

    @property
    def badge_estado(self):
        mapping = {
            'pendiente': 'badge-danger',
            'en_curso': 'badge-warning',
            'implementada': 'badge-success',
            'verificada': 'badge-success',
            'continua': 'badge-secondary',
        }
        return mapping.get(self.estado, 'badge-secondary')

    @property
    def badge_tipo(self):
        mapping = {
            'evitables': 'badge-danger',
            'monitorizables': 'badge-warning',
            'no_evitables': 'badge-secondary',
        }
        return mapping.get(self.tipo_factor_riesgo, 'badge-secondary')

    @property
    def tiene_riesgo_elevado(self):
        return self.gr in ('M', 'A')
