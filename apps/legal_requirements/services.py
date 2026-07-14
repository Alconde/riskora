from datetime import date, timedelta

from django.db.models import Count, Q

from .models import AlertaLegal, CumplimientoLegal


NORMATIVA_PRL_ESPANOLA = [
    {
        'tipo': 'ley',
        'numero': '31/1995',
        'nombre': 'Ley 31/1995, de 8 de noviembre, de Prevención de Riesgos Laborales',
        'fecha_publicacion': '1995-11-09',
        'fecha_vigencia': '1995-02-12',
        'ambito': 'estatal',
        'resumen': 'Ley marco de PRL. Define derechos y obligaciones, Evaluación de Riesgos, Planificación, Información, Formación y Vigilancia de la Salud.',
    },
    {
        'tipo': 'real_decreto',
        'numero': '39/1997',
        'nombre': 'Real Decreto 39/1997, de 31 de enero, Reglamento de los Servicios de Prevención',
        'fecha_publicacion': '1997-02-08',
        'fecha_vigencia': '1997-02-08',
        'ambito': 'estatal',
        'resumen': 'Regula los Servicios de Prevención: organización, funciones, medios materiales y formación del personal. Base para la evaluación de riesgos y planes de prevención.',
    },
    {
        'tipo': 'real_decreto',
        'numero': '486/1997',
        'nombre': 'Real Decreto 486/1997, de 14 de abril, sobre disposiciones mínimas de seguridad en lugares de trabajo',
        'fecha_publicacion': '1997-04-15',
        'fecha_vigencia': '1997-04-15',
        'ambito': 'estatal',
        'resumen': 'Condiciones de seguridad en espacios de trabajo: iluminación, ventilación, temperatura, suelos, vías de circulación, escaleras, barandillas, riesgos específicos.',
    },
    {
        'tipo': 'real_decreto',
        'numero': '140/2003',
        'nombre': 'Real Decreto 140/2003, de 7 de febrero, normas de sanidad en los centros de trabajo',
        'fecha_publicacion': '2003-02-08',
        'fecha_vigencia': '2003-02-08',
        'ambito': 'estatal',
        'resumen': 'Condiciones sanitarias en centros de trabajo: instalaciones, servicios higiénicos, vestuarios, comedores, agua potable, eliminación de residuos.',
    },
    {
        'tipo': 'real_decreto',
        'numero': '2177/2004',
        'nombre': 'Real Decreto 2177/2004, sobre disposiciones mínimas de seguridad contra riesgos de explosión',
        'fecha_publicacion': '2004-11-27',
        'fecha_vigencia': '2004-11-27',
        'ambito': 'estatal',
        'resumen': 'Protección contra explosiones: evaluación de riesgos, zonas ATEX, equipos y protección. Transpone Directiva 1999/92/CE.',
    },
    {
        'tipo': 'real_decreto',
        'numero': '156/2010',
        'nombre': 'Real Decreto 156/2010, sobre equipos de trabajo',
        'fecha_publicacion': '2010-02-19',
        'fecha_vigencia': '2010-02-19',
        'ambito': 'estatal',
        'resumen': 'Requisitos de equipos de trabajo: instalación, uso, mantenimiento, inspección, reparación. Equipos levantadores, de elevación y transporte.',
    },
    {
        'tipo': 'real_decreto',
        'numero': '1215/1997',
        'nombre': 'Real Decreto 1215/1997, sobre disposiciones mínimas de seguridad en manipulación manual de cargas',
        'fecha_publicacion': '1997-05-24',
        'fecha_vigencia': '1997-05-24',
        'ambito': 'estatal',
        'resumen': 'Protección frente a riesgos por manipulación manual de cargas. Limites de peso, evaluación de riesgos, medidas preventivas.',
    },
    {
        'tipo': 'real_decreto',
        'numero': '116/2002',
        'nombre': 'Real Decreto 116/2002, sobre disposiciones mínimas de seguridad en trabajos con riesgo de caída',
        'fecha_publicacion': '2002-02-01',
        'fecha_vigencia': '2002-02-01',
        'ambito': 'estatal',
        'resumen': 'Trabajos en altura: evaluación, medidas preventivas, sistemas de protección contra caídas, andamios, plataformas elevadoras.',
    },
    {
        'tipo': 'real_decreto',
        'numero': '664/1997',
        'nombre': 'Real Decreto 664/1997, sobre protección de trabajadores contra riesgos derivados de exposición a agentes biológicos',
        'fecha_publicacion': '1997-05-10',
        'fecha_vigencia': '1997-05-10',
        'ambito': 'estatal',
        'resumen': 'Evaluación y prevención de riesgos por agentes biológicos: clasificación, medidas higiénicas, vigilancia sanitaria.',
    },
    {
        'tipo': 'real_decreto',
        'numero': '374/2001',
        'nombre': 'Real Decreto 374/2001, sobre protección de trabajadores contra riesgos derivados de agentes químicos',
        'fecha_publicacion': '2001-04-04',
        'fecha_vigencia': '2001-04-04',
        'ambito': 'estatal',
        'resumen': 'Evaluación de riesgos por agentes químicos, medidas preventivas, EPIs, vigilancia sanitaria. Transpone Directiva 98/24/CE.',
    },
    {
        'tipo': 'real_decreto',
        'numero': '1027/2007',
        'nombre': 'Real Decreto 1027/2007, sobre instalaciones eléctricas (REBT)',
        'fecha_publicacion': '2007-07-20',
        'fecha_vigencia': '2007-07-20',
        'ambito': 'estatal',
        'resumen': 'Reglamento Electrotécnico para Baja Tensión: instalaciones eléctricas en centros de trabajo, protecciones, verificaciones.',
    },
    {
        'tipo': 'real_decreto',
        'numero': '614/2001',
        'nombre': 'Real Decreto 614/2001, sobre disposiciones mínimas de protección contra riesgos eléctricos',
        'fecha_publicacion': '2001-04-28',
        'fecha_vigencia': '2001-04-28',
        'ambito': 'estatal',
        'resumen': 'Riesgos eléctricos en centros de trabajo: evaluación, protección, mantenimiento, señalización, trabajos sin tensión.',
    },
    {
        'tipo': 'real_decreto',
        'numero': '84/2015',
        'nombre': 'Real Decreto 84/2015, sobre equipos de protección individual',
        'fecha_publicacion': '2015-01-30',
        'fecha_vigencia': '2015-01-30',
        'ambito': 'estatal',
        'resumen': 'Selección, uso y mantenimiento de EPIs: evaluación de riesgos, formación, marcado CE, registro de entrega.',
    },
    {
        'tipo': 'real_decreto',
        'numero': '604/2004',
        'nombre': 'Real Decreto 604/2004, sobre disposiciones mínimas de seguridad en maquinaria',
        'fecha_publicacion': '2004-03-06',
        'fecha_vigencia': '2004-03-06',
        'ambito': 'estatal',
        'resumen': 'Prevención de riesgos por maquinaria: evaluación, protección, dispositivos de seguridad, señalización.',
    },
    {
        'tipo': 'real_decreto',
        'numero': '773/1997',
        'nombre': 'Real Decreto 773/1997, sobre disposiciones mínimas de seguridad en trabajos con riesgo de incendio',
        'fecha_publicacion': '1997-04-30',
        'fecha_vigencia': '1997-04-30',
        'ambito': 'estatal',
        'resumen': 'Prevención de incendios en centros de trabajo: evaluación, protección contra fuego, planes de emergencia.',
    },
    {
        'tipo': 'real_decreto',
        'numero': '1620/1997',
        'nombre': 'Real Decreto 1620/1997, sobre normas de higiene para la prevención de riesgos por agents químicos',
        'fecha_publicacion': '1997-05-31',
        'fecha_vigencia': '1997-05-31',
        'ambito': 'estatal',
        'resumen': 'Valores límite de exposición profesional, métodos de medición, vigilancia médica.',
    },
    {
        'tipo': 'real_decreto',
        'numero': '513/2017',
        'nombre': 'Real Decreto 513/2017, sobre protección de trabajadores contra riesgos por曝露 a campos magnéticos',
        'fecha_publicacion': '2017-07-05',
        'fecha_vigencia': '2017-07-05',
        'ambito': 'estatal',
        'resumen': 'Prevención de riesgos por曝vesp a campos magnéticos en el trabajo. Transpone Directiva 2013/35/UE.',
    },
    {
        'tipo': 'orden',
        'numero': '335/2020',
        'nombre': 'Orden SND/335/2020, sobre planes de contingencia en empresas durante la crisis COVID-19',
        'fecha_publicacion': '2020-03-20',
        'fecha_vigencia': '2020-03-20',
        'ambito': 'estatal',
        'resumen': 'Medidas sanitarias específicas para centros de trabajo durante la crisis del COVID-19.',
    },
]


def get_requisitos_por_categoria(categoria):
    """Devuelve los requisitos tipicos de una categoria de normativa."""
    REQUISITOS_TIPO = {
        'prevencion': [
            'Evaluación de riesgos general',
            'Plan de prevención actualizado',
            'Designación de responsables de PRL',
            'Plan de emergencia y evacuación',
            'Protocolos de seguridad por puesto',
        ],
        'formacion': [
            'Formación básica en PRL para todos los trabajadores',
            'Formación específica por puesto de trabajo',
            'Formación en emergencias y primeros auxilios',
            'Certificados de formación actualizados',
        ],
        'vigilancia': [
            'Programa de vigilancia de la salud',
            'Informes médicos de aptitud',
            'Vigilancia específica por exposición a agentes',
            'Registro de vigilancia actualizado',
        ],
        'epis': [
            'Evaluación de riesgos para selección de EPIs',
            'EPIs homologados y con marcado CE',
            'Registro de entrega de EPIs',
            'Mantenimiento y sustitución de EPIs',
            'Formación en uso correcto de EPIs',
        ],
        'instalaciones': [
            'Verificación de instalaciones eléctricas',
            'Mantenimiento preventivo de maquinaria',
            'Señalización de seguridad actualizada',
            'Verificación de equipos de elevación',
        ],
        'emergencias': [
            'Plan de emergencia y evacuación',
            'Brigadas de emergencia formadas',
            'Equipos de extintores revisados',
            'Simulacros de evacuación realizados',
            'Botiquín de primeros auxilios',
        ],
        'documentacion': [
            'Evaluación de riesgos documentada',
            'Plan de prevención por escrito',
            'Procedimientos de trabajo seguros',
            'Registro de accidentes y incidentes',
            'Actas de comités de seguridad',
        ],
        'notificacion': [
            'Comunicación de apertura del centro',
            'Notificación de accidentes graves',
            'Designación de servicios de prevención',
            'Contratación de EPIS para vigilantes',
        ],
    }
    return REQUISITOS_TIPO.get(categoria, [])


def get_cumplimiento_empresa(empresa):
    """Resumen del cumplimiento legal de una empresa."""
    total = CumplimientoLegal.objects.filter(empresa=empresa).count()
    if total == 0:
        return {
            'total': 0,
            'cumple': 0,
            'no_cumple': 0,
            'en_curso': 0,
            'pendiente': 0,
            'no_aplica': 0,
            'porcentaje_cumplimiento': 0,
        }
    conteo = CumplimientoLegal.objects.filter(empresa=empresa).aggregate(
        cumple=Count('id', filter=Q(estado='cumple')),
        no_cumple=Count('id', filter=Q(estado='no_cumple')),
        en_curso=Count('id', filter=Q(estado='en_curso')),
        pendiente=Count('id', filter=Q(estado='pendiente')),
        no_aplica=Count('id', filter=Q(estado='no_aplica')),
    )
    evaluados = total - conteo['pendiente'] - conteo['no_aplica']
    conteo['total'] = total
    conteo['porcentaje_cumplimiento'] = (
        round(conteo['cumple'] / evaluados * 100) if evaluados > 0 else 0
    )
    return conteo


def get_alertas_legales(empresa, dias=30):
    """Alertas legales pendientes (no leídas y no resueltas)."""
    return AlertaLegal.objects.filter(
        empresa=empresa,
        leida=False,
        resuelta=False,
    ).select_related('cumplimiento', 'normativa')


def get_cumplimientos_vencidos(empresa):
    """Cumplimientos con revisión vencida."""
    from datetime import date
    return CumplimientoLegal.objects.filter(
        empresa=empresa,
        fecha_proxima_revision__lt=date.today(),
        estado__in=['no_cumple', 'pendiente'],
    ).select_related('requisito', 'requisito__normativa')


def get_cumplimientos_proximos(empresa, dias=30):
    """Cumplimientos con revisión en los próximos N días."""
    from datetime import date
    hoy = date.today()
    limite = hoy + timedelta(days=dias)
    return CumplimientoLegal.objects.filter(
        empresa=empresa,
        fecha_proxima_revision__gte=hoy,
        fecha_proxima_revision__lte=limite,
    ).select_related('requisito', 'requisito__normativa')
