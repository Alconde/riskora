from django.db import models


def generar_codigo_eepp(empresa):
    from django.utils import timezone
    year = timezone.localdate().year
    from .models import EnfermedadProfesional
    count = (
        EnfermedadProfesional.objects.filter(
            empresa=empresa, fecha_diagnostico__year=year
        ).count() + 1
    )
    return f'EEPP-{year}-{count:03d}'


def calcular_estadisticas_eepp(empresa=None):
    from .models import EnfermedadProfesional

    qs = EnfermedadProfesional.objects.all()
    if empresa:
        qs = qs.filter(empresa=empresa)

    total = qs.count()
    abiertas = qs.filter(estado='abierto').count()
    en_investigacion = qs.filter(estado='en_investigacion').count()
    cerradas = qs.filter(estado='cerrado').count()
    graves = qs.filter(gravedad__in=['grave', 'muy_grave']).count()
    por_agente = {}
    for choice in EnfermedadProfesional.AgenteCausante.choices:
        agente_val = choice[0]
        agente_label = choice[1]
        count = qs.filter(agente_causante=agente_val).count()
        if count > 0:
            por_agente[agente_label] = count

    return {
        'total': total,
        'abiertas': abiertas,
        'en_investigacion': en_investigacion,
        'cerradas': cerradas,
        'graves': graves,
        'por_agente': por_agente,
        'tasa_cierre': (
            f'{round((cerradas / total) * 100)}%' if total else '0%'
        ),
    }


def generar_pdf_eepp_blanco(buffer):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title2', parent=styles['Title'], fontSize=16)
    section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=12, spaceAfter=6, spaceBefore=12, textColor=colors.HexColor('#0f766e'))
    normal = ParagraphStyle('Normal2', parent=styles['Normal'], fontSize=10)
    small = ParagraphStyle('Small', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#64748b'))

    elements.append(Paragraph('FORMULARIO DE INVESTIGACION DE ENFERMEDADES PROFESIONALES', title_style))
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(Paragraph('Riskora - Prevencion de Riesgos Laborales', small))
    elements.append(Spacer(1, 0.5 * cm))

    sections = [
        ('DATOS DE LA ENFERMEDAD PROFESIONAL', [
            ['Codigo de la EEPP:', ''],
            ['Fecha de diagnostico:', ''],
            ['Centro de trabajo:', ''],
            ['Nombre de la enfermedad:', ''],
            ['Agente causante:', ''],
            ['Tipo de exposicion:', ''],
            ['Duracion de la exposicion:', ''],
            ['Parte del cuerpo afectada:', ''],
            ['Gravedad:', ''],
        ]),
        ('DATOS DEL TRABAJADOR', [
            ['Nombre del trabajador:', ''],
            ['Puesto de trabajo:', ''],
            ['Horas trabajadas (1-8):', ''],
            ['Hora del dia:', ''],
            ['Edad:', ''],
            ['Tiempo en el puesto:', ''],
        ]),
        ('INVESTIGACION', [
            ['Fecha de inicio investigacion:', ''],
            ['Metodologia:', ''],
            ['Investigador:', ''],
            ['Revisor:', ''],
            ['Acto o condicion detectada:', ''],
            ['Riesgo identificado:', ''],
        ]),
        ('DESCRIPCION', [
            ['Descripcion ideal (que deberia haber pasado):', ''],
            ['', ''],
            ['Descripcion real (que realmente paso):', ''],
            ['', ''],
        ]),
        ('ANALISIS DE CAUSAS', [
            ['Causas inmediatas:', ''],
            ['', ''],
            ['Causas basicas:', ''],
            ['', ''],
            ['Causas organizativas:', ''],
            ['', ''],
        ]),
        ('MEDIDAS PREVENTIVAS', [
            ['Medidas propuestas:', ''],
            ['', ''],
            ['Plazo:', ''],
            ['Responsable:', ''],
            ['Coste:', ''],
            ['Riesgo registrado en la ER:', ''],
        ]),
        ('CONCLUSIONES Y FIRMA', [
            ['Conclusiones:', ''],
            ['', ''],
            ['Fecha de firma:', ''],
            ['Firma investigador:', ''],
            ['Firma revisor:', ''],
        ]),
    ]

    for section_title, rows in sections:
        elements.append(Paragraph(section_title, section_style))
        for label, value in rows:
            elements.append(Paragraph(f'<b>{label}</b> {value}', normal))
            elements.append(Spacer(1, 0.2 * cm))
        elements.append(Spacer(1, 0.3 * cm))

    doc.build(elements)


def generar_pdf_eepp(investigacion, buffer):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

    eepp = investigacion.enfermedad
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title2', parent=styles['Title'], fontSize=14)
    section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=12, spaceAfter=6, spaceBefore=12, textColor=colors.HexColor('#0f766e'))
    normal = ParagraphStyle('Normal2', parent=styles['Normal'], fontSize=10)
    small = ParagraphStyle('Small', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#64748b'))

    elements.append(Paragraph(f'INVESTIGACION EEPP - {eepp.codigo}', title_style))
    elements.append(Spacer(1, 0.3 * cm))
    empresa_name = eepp.empresa.legal_name if eepp.empresa else ''
    elements.append(Paragraph(f'{empresa_name} | {eepp.titulo}', small))
    elements.append(Spacer(1, 0.5 * cm))

    def field(label, value):
        return Paragraph(f'<b>{label}:</b> {value or "-"}', normal)

    def section(title):
        elements.append(Paragraph(title, section_style))

    section('DATOS DE LA ENFERMEDAD PROFESIONAL')
    elements.append(field('Codigo', eepp.codigo))
    elements.append(field('Fecha de diagnostico', str(eepp.fecha_diagnostico)))
    elements.append(field('Centro de trabajo', str(eepp.centro_trabajo)))
    elements.append(field('Nombre de la enfermedad', eepp.nombre_enfermedad))
    elements.append(field('Agente causante', eepp.get_agente_causante_display()))
    elements.append(field('Tipo de exposicion', eepp.tipo_exposicion))
    elements.append(field('Duracion de la exposicion', eepp.duracion_exposicion))
    elements.append(field('Parte del cuerpo', eepp.parte_cuerpo))
    elements.append(field('Gravedad', eepp.get_gravedad_display()))
    elements.append(Spacer(1, 0.3 * cm))

    section('DATOS DEL TRABAJADOR')
    elements.append(field('Nombre', str(eepp.trabajador_afectado) if eepp.trabajador_afectado else '-'))
    elements.append(field('Puesto de trabajo', investigacion.puesto_trabajo))
    elements.append(field('Horas trabajadas', str(investigacion.horas_trabajador) if investigacion.horas_trabajador else '-'))
    elements.append(field('Hora del dia', str(investigacion.hora_dia) if investigacion.hora_dia else '-'))
    elements.append(field('Edad', str(investigacion.edad) if investigacion.edad else '-'))
    elements.append(field('Tiempo en el puesto', investigacion.tiempo_puesto))
    elements.append(Spacer(1, 0.3 * cm))

    section('INVESTIGACION')
    elements.append(field('Fecha de inicio', str(investigacion.fecha_inicio)))
    elements.append(field('Metodologia', investigacion.get_metodologia_display()))
    elements.append(field('Investigador', str(investigacion.investigador) if investigacion.investigador else '-'))
    elements.append(field('Revisor', str(investigacion.revisor) if investigacion.revisor else '-'))
    elements.append(field('Acto/condicion detectada', investigacion.acto_condicion_detectada))
    elements.append(field('Riesgo identificado', investigacion.get_riesgo_identificado_display()))
    elements.append(Spacer(1, 0.3 * cm))

    section('DESCRIPCION')
    elements.append(field('Descripcion ideal (que deberia haber pasado)', investigacion.descripcion_ideal))
    elements.append(field('Descripcion real (que realmente paso)', investigacion.descripcion_real))
    elements.append(Spacer(1, 0.3 * cm))

    section('ANALISIS DE CAUSAS')
    elements.append(field('Causas inmediatas', investigacion.causas_inmediatas))
    elements.append(field('Causas basicas', investigacion.causas_basicas))
    elements.append(field('Causas organizativas', investigacion.causas_organizativas))
    elements.append(Spacer(1, 0.3 * cm))

    section('MEDIDAS PREVENTIVAS')
    elements.append(field('Medidas propuestas', investigacion.medidas_preventivas))
    elements.append(field('Plazo', str(investigacion.plazo) if investigacion.plazo else '-'))
    elements.append(field('Responsable', str(investigacion.responsable) if investigacion.responsable else '-'))
    coste_str = f'{investigacion.coste} EUR' if investigacion.coste else '-'
    elements.append(field('Coste', coste_str))
    er_str = 'Si' if investigacion.riesgo_en_er else 'No'
    elements.append(field('Riesgo registrado en la ER', er_str))
    elements.append(Spacer(1, 0.3 * cm))

    section('CONCLUSIONES Y FIRMA')
    elements.append(field('Conclusiones', investigacion.conclusiones))
    elements.append(field('Fecha de firma', str(investigacion.fecha_firma) if investigacion.fecha_firma else '-'))
    elements.append(field('Estado', investigacion.get_estado_display()))
    elements.append(Spacer(1, 1 * cm))

    elements.append(Paragraph('________________________', normal))
    elements.append(Paragraph('Firma investigador', small))

    doc.build(elements)
