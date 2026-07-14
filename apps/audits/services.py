from datetime import date

from django.db.models import Count, Q

from .models import AuditoriaInterna, ChecklistAuditoria


def get_checklist_plantilla(empresa=None):
    """Devuelve la plantilla completa de checklist ISO 45001:2018 para auditoría."""
    return CHECKLIST_ISO_45001


CHECKLIST_ISO_45001 = [
    {'id': 1, 'clausula': '4.1', 'seccion': 'Contexto', 'requisito': 'Comprender la organización y su contexto', 'evidencia_requerida': 'Análisis FODA, mapas de procesos, organigrama'},
    {'id': 2, 'clausula': '4.2', 'seccion': 'Contexto', 'requisito': 'Comprender las necesidades y expectativas de las partes interesadas', 'evidencia_requerida': 'Registro de partes interesadas, análisis de requisitos legales'},
    {'id': 3, 'clausula': '4.3', 'seccion': 'Contexto', 'requisito': 'Determinar el alcance del SM-SST', 'evidencia_requerida': 'Documento de alcance aprobado'},
    {'id': 4, 'clausula': '4.4', 'seccion': 'Contexto', 'requisito': 'Sistema de gestión de la SST', 'evidencia_requerida': 'Manual del sistema, mapas de procesos'},
    {'id': 5, 'clausula': '5.1', 'seccion': 'Liderazgo', 'requisito': 'Liderazgo y compromiso', 'evidencia_requerida': 'Declaración de política firmada por alta dirección'},
    {'id': 6, 'clausula': '5.2', 'seccion': 'Liderazgo', 'requisito': 'Política de SST', 'evidencia_requerida': 'Política documentada, comunicada, disponible'},
    {'id': 7, 'clausula': '5.3', 'seccion': 'Liderazgo', 'requisito': 'Roles, responsabilidades y autoridades', 'evidencia_requerida': 'Organigrama PRL, fichas de puesto, delegaciones'},
    {'id': 8, 'clausula': '5.4', 'seccion': 'Liderazgo', 'requisito': 'Consultación y participación de los trabajadores', 'evidencia_requerida': 'Actas de comités de seguridad, encuestas de satisfacción'},
    {'id': 9, 'clausula': '6.1.1', 'seccion': 'Planificación', 'requisito': 'Acciones para abordar riesgos y oportunidades', 'evidencia_requerida': 'Matriz de riesgos, plan de acción PRL'},
    {'id': 10, 'clausula': '6.1.2', 'seccion': 'Planificación', 'requisito': 'Identificación de peligros y evaluación de riesgos', 'evidencia_requerida': 'Evaluación de riesgos vigente, fichas de peligros'},
    {'id': 11, 'clausula': '6.1.3', 'seccion': 'Planificación', 'requisito': 'Determinación de requisitos legales', 'evidencia_requerida': 'Registro de normativa PRL, auditoría legal'},
    {'id': 12, 'clausula': '6.1.4', 'seccion': 'Planificación', 'requisito': 'Planificación de acciones', 'evidencia_requerida': 'Planes de acción con responsable y fecha'},
    {'id': 13, 'clausula': '6.2.1', 'seccion': 'Objetivos', 'requisito': 'Objetivos de SST', 'evidencia_requerida': 'Objetivos medibles documentados, plan de mejora'},
    {'id': 14, 'clausula': '6.2.2', 'seccion': 'Objetivos', 'requisito': 'Planificación de acciones para lograr objetivos', 'evidencia_requerida': 'Programa de gestión PRL con indicadores'},
    {'id': 15, 'clausula': '7.1', 'seccion': 'Apoyo', 'requisito': 'Recursos', 'evidencia_requerida': 'Presupuesto PRL, EPIs, medios materiales'},
    {'id': 16, 'clausula': '7.2', 'seccion': 'Apoyo', 'requisito': 'Competencia', 'evidencia_requerida': 'Certificados formación PRL, NTPs, cursos'},
    {'id': 17, 'clausula': '7.3', 'seccion': 'Apoyo', 'requisito': 'Toma de conciencia', 'evidencia_requerida': 'Listas de asistencia formación, pruebas evaluación'},
    {'id': 18, 'clausula': '7.4', 'seccion': 'Apoyo', 'requisito': 'Comunicación', 'evidencia_requerida': 'Canales de comunicación PRL, cartelera, reuniones'},
    {'id': 19, 'clausula': '7.5', 'seccion': 'Apoyo', 'requisito': 'Información documentada', 'evidencia_requerida': 'Procedimientos, registros, maquinaria documental'},
    {'id': 20, 'clausula': '8.1.1', 'seccion': 'Operación', 'requisito': 'Planificación operativa y control', 'evidencia_requerida': 'Procedimientos operativos PRL, PTTL'},
    {'id': 21, 'clausula': '8.1.2', 'seccion': 'Operación', 'requisito': 'Eliminación de peligros y reducción de riesgos', 'evidencia_requerida': 'Evaluación de riesgos, medidas preventivas'},
    {'id': 22, 'clausula': '8.1.3', 'seccion': 'Operación', 'requisito': 'Control de cambios', 'evidencia_requerida': 'Procedimiento de gestión del cambio, registros'},
    {'id': 23, 'clausula': '8.1.4', 'seccion': 'Operación', 'requisito': 'Adquisición', 'evidencia_requerida': 'Evaluación de proveedores, cláusulas contractuales PRL'},
    {'id': 24, 'clausula': '8.2', 'seccion': 'Operación', 'requisito': 'Preparación y respuesta ante emergencias', 'evidencia_requerida': 'Plan de emergencias, simulacros, brigadas'},
    {'id': 25, 'clausula': '9.1.1', 'seccion': 'Evaluación', 'requisito': 'Seguimiento, medición, análisis y evaluación', 'evidencia_requerida': 'Indicadores KPI SST, cuadros de mando'},
    {'id': 26, 'clausula': '9.1.2', 'seccion': 'Evaluación', 'requisito': 'Evaluación del cumplimiento legal', 'evidencia_requerida': 'Auditoría legal PRL, actualización normativa'},
    {'id': 27, 'clausula': '9.2', 'seccion': 'Evaluación', 'requisito': 'Auditoría interna', 'evidencia_requerida': 'Programa de auditorías, informes internos'},
    {'id': 28, 'clausula': '9.3', 'seccion': 'Evaluación', 'requisito': 'Revisión por la dirección', 'evidencia_requerida': 'Actas de revisión dirección, planes de mejora'},
    {'id': 29, 'clausula': '10.1', 'seccion': 'Mejora', 'requisito': 'No conformidad y acción correctiva', 'evidencia_requerida': 'Registro NCs, análisis causa raíz, acciones'},
    {'id': 30, 'clausula': '10.2', 'seccion': 'Mejora', 'requisito': 'Mejora continua', 'evidencia_requerida': 'Plan de mejora continua, sugerencias'},
]


def get_resumen_checklist(auditoria):
    """Devuelve un diccionario con el resumen de la auditoría."""
    items = auditoria.checklist.all()
    total = items.count()
    evaluados = items.exclude(conformidad='').exclude(conformidad='no_aplica').count()

    return {
        'total': total,
        'evaluados': evaluados,
        'conformes': items.filter(conformidad='conforme').count(),
        'no_conformes': items.filter(conformidad='no_conforme').count(),
        'observaciones': items.filter(conformidad='observacion').count(),
        'no_aplican': items.filter(conformidad='no_aplica').count(),
        'pendientes': items.filter(conformidad='').count(),
        'porcentaje_cumplimiento': (
            round(items.filter(conformidad='conforme').count() / evaluados * 100)
            if evaluados > 0
            else 0
        ),
    }


def get_programa_resumen(programa):
    """Resumen del programa de auditorías anual."""
    auditorias = programa.auditorias.all()
    total = auditorias.count()
    nc_total = 0
    for aud in auditorias.all():
        nc_total += aud.checklist.filter(conformidad='no_conforme').count()

    return {
        'total_auditorias': total,
        'completadas': auditorias.filter(estado='completada').count(),
        'en_curso': auditorias.filter(estado='en_curso').count(),
        'planificadas': auditorias.filter(estado='planificada').count(),
        'nc_total': nc_total,
        'porcentaje_avance': programa.porcentaje_avance,
    }


def get_auditorias_pendientes(empresa, dias=30):
    """Auditorías planificadas en los próximos N días."""
    hoy = date.today()
    limite = hoy + __import__('datetime').timedelta(days=dias)
    return AuditoriaInterna.objects.filter(
        empresa=empresa,
        estado='planificada',
        fecha_planificada__gte=hoy,
        fecha_planificada__lte=limite,
    )


def get_dashboard_auditorias(empresa):
    """Contexto completo de auditorías para el dashboard principal."""
    hoy = date.today()
    from django.utils import timezone

    auditorias_pendientes = AuditoriaInterna.objects.filter(
        empresa=empresa,
        estado__in=['planificada', 'en_curso'],
    ).select_related('programa')

    nc_abiertas = ChecklistAuditoria.objects.filter(
        auditoria__empresa=empresa,
        conformidad='no_conforme',
        cerrado=False,
    ).count()

    auditorias_proximas = auditorias_pendientes.filter(
        fecha_planificada__gte=hoy,
        fecha_planificada__lte=hoy + __import__('datetime').timedelta(days=30),
    )

    return {
        'auditorias_pendientes_count': auditorias_pendientes.count(),
        'nc_abiertas_count': nc_abiertas,
        'auditorias_proximas': auditorias_proximas[:5],
    }
