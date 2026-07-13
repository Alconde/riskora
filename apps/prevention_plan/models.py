from django.db import models
from apps.companies.models import Company


SI_NO_NO_APLICA = [
    ('si', 'Si'),
    ('no', 'No'),
    ('no_aplica', 'No aplica'),
]


def upload_politica_path(instance, filename):
    return f'plan_prevencion/{instance.company_id}/politica/{filename}'


def upload_organigrama_path(instance, filename):
    return f'plan_prevencion/{instance.company_id}/organigrama/{filename}'


def upload_doc_delegado_path(instance, filename):
    return f'plan_prevencion/{instance.company_id}/delegado/{filename}'


def upload_doc_recurso_path(instance, filename):
    return f'plan_prevencion/{instance.company_id}/recurso/{filename}'


DEFAULT_ORGANIGRAMA = (
    'Estructura organizativa:\n\n'
    '1. Empresario / Direction General\n'
    '   - Responsable maximo de la empresa\n'
    '   - Aprueba el Plan de Prevencion\n\n'
    '2. Encargado / Mando intermedio\n'
    '   - Supervisa la actividad preventiva en su area\n'
    '   - Aplica las medidas preventivas\n\n'
    '3. Trabajadores/as\n'
    '   - Cumplen las normas de seguridad e higiene\n'
    '   - Colaboran en la prevencion de riesgos'
)

DEFAULT_FUNCIONES = (
    'Funciones y responsabilidades segun el organigrama:\n\n'
    'EMPRESARIO/DIRECCION:\n'
    '- Aprobar y revisar el Plan de Prevencion\n'
    '- Dotar los medios necesarios para la prevencion\n'
    '- Garantizar la formacion de los trabajadores\n'
    '- Designar al delegado de prevencion y recurso preventivo\n\n'
    'ENCARGADO/MANDO INTERMEDIO:\n'
    '- Supervisar el cumplimiento de las medidas preventivas\n'
    '- Informar de los riesgos a los trabajadores\n'
    '- Colaborar en la evaluacion de riesgos\n'
    '- Formar a los trabajadores nuevos\n\n'
    'TRABAJADORES/AS:\n'
    '- Cumplir las normas de seguridad e higiene\n'
    '- Usar correctamente los EPIs\n'
    '- Informar de las situaciones de riesgo\n'
    '- Colaborar en la prevencion de riesgos'
)


class PlanPrevention(models.Model):
    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name='prevention_plan',
        verbose_name='Empresa',
    )

    # Politica
    politica = models.FileField(
        upload_to=upload_politica_path,
        blank=True,
        null=True,
        verbose_name='Politica de prevencion (PDF)',
    )
    politica_fecha_subida = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de subida de politica',
    )
    politica_firmada = models.BooleanField(
        default=False,
        verbose_name='Politica firmada',
    )

    # Organigrama
    organigrama = models.FileField(
        upload_to=upload_organigrama_path,
        blank=True,
        null=True,
        verbose_name='Organigrama (PDF/Imagen)',
    )
    organigrama_texto = models.TextField(
        default=DEFAULT_ORGANIGRAMA,
        verbose_name='Texto del organigrama',
    )

    # Delegado de PRL
    delegado_prl = models.CharField(
        max_length=20,
        choices=SI_NO_NO_APLICA,
        default='no_aplica',
        verbose_name='Delegado de PRL',
    )
    delegado_fecha_designacion = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha designacion delegado',
    )
    delegado_formacion = models.BooleanField(
        default=False,
        verbose_name='Delegado con formacion',
    )
    doc_designacion_delegado = models.FileField(
        upload_to=upload_doc_delegado_path,
        blank=True,
        null=True,
        verbose_name='Doc. designacion delegado',
    )
    doc_formacion_delegado = models.FileField(
        upload_to=upload_doc_delegado_path,
        blank=True,
        null=True,
        verbose_name='Doc. formacion delegado',
    )

    # Recurso Preventivo
    recurso_preventivo = models.CharField(
        max_length=20,
        choices=SI_NO_NO_APLICA,
        default='no_aplica',
        verbose_name='Recurso preventivo',
    )
    recurso_actividades = models.TextField(
        blank=True,
        default='',
        verbose_name='Actividades en las que se requiere recurso preventivo',
    )
    recurso_fecha_designacion = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha designacion recurso preventivo',
    )
    recurso_formacion = models.BooleanField(
        default=False,
        verbose_name='Recurso preventivo con formacion',
    )
    doc_designacion_recurso = models.FileField(
        upload_to=upload_doc_recurso_path,
        blank=True,
        null=True,
        verbose_name='Doc. designacion recurso preventivo',
    )
    doc_formacion_recurso = models.FileField(
        upload_to=upload_doc_recurso_path,
        blank=True,
        null=True,
        verbose_name='Doc. formacion recurso preventivo',
    )

    # Funciones y responsabilidades
    funciones_responsabilidades = models.TextField(
        default=DEFAULT_FUNCIONES,
        verbose_name='Funciones y responsabilidades',
    )

    # ETT
    utiliza_ett = models.BooleanField(
        default=False,
        verbose_name='Utiliza empresas de ETT',
    )
    puestos_ett = models.TextField(
        blank=True,
        default='',
        verbose_name='Puestos cubiertos por ETT',
    )

    # Teletrabajo
    tiene_teletrabajo = models.BooleanField(
        default=False,
        verbose_name='Tiene trabajadores en teletrabajo',
    )
    puestos_teletrabajo = models.TextField(
        blank=True,
        default='',
        verbose_name='Puestos en teletrabajo',
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Plan de Prevencion'
        verbose_name_plural = 'Planes de Prevencion'
        ordering = ['company']

    def __str__(self):
        return f'Plan de Prevencion - {self.company}'

    @property
    def politica_estado(self):
        if self.politica:
            return 'completo'
        return 'pendiente'

    @property
    def organigrama_estado(self):
        if self.organigrama or self.organigrama_texto:
            return 'completo'
        return 'pendiente'

    @property
    def delegado_estado(self):
        if self.delegado_prl == 'no_aplica':
            return 'no_aplica'
        if self.delegado_prl == 'si' and self.delegado_fecha_designacion:
            return 'completo'
        if self.delegado_prl == 'no':
            return 'completo'
        return 'pendiente'

    @property
    def recurso_estado(self):
        if self.recurso_preventivo == 'no_aplica':
            return 'no_aplica'
        if self.recurso_preventivo == 'si' and self.recurso_fecha_designacion:
            return 'completo'
        if self.recurso_preventivo == 'no':
            return 'completo'
        return 'pendiente'

    @property
    def funciones_estado(self):
        if self.funciones_responsabilidades:
            return 'completo'
        return 'pendiente'

    @property
    def ett_estado(self):
        if not self.utiliza_ett:
            return 'completo'
        if self.utiliza_ett and self.puestos_ett:
            return 'completo'
        return 'pendiente'

    @property
    def teletrabajo_estado(self):
        if not self.tiene_teletrabajo:
            return 'completo'
        if self.tiene_teletrabajo and self.puestos_teletrabajo:
            return 'completo'
        return 'pendiente'

    @property
    def progreso_total(self):
        estados = [
            self.politica_estado,
            self.organigrama_estado,
            self.delegado_estado,
            self.recurso_estado,
            self.funciones_estado,
            self.ett_estado,
            self.teletrabajo_estado,
        ]
        completos = sum(1 for e in estados if e == 'completo')
        aplicables = sum(1 for e in estados if e != 'no_aplica')
        if aplicables == 0:
            return 100
        return round((completos / aplicables) * 100)
