from .models import Inspeccion


def generar_nc_desde_item(item, user):
    from apps.corrective_actions.models import NoConformidad
    from apps.corrective_actions.services import generar_codigo_nc

    inspeccion = item.inspeccion
    nc = NoConformidad.objects.create(
        empresa=inspeccion.empresa,
        codigo=generar_codigo_nc(inspeccion.empresa),
        titulo=f'NC desde inspeccion INS-{inspeccion.pk:04d}: {item.descripcion[:100]}',
        descripcion=f'Item de inspeccion no conforme:\n\n{item.descripcion}\n\nObservaciones: {item.observaciones or "Ninguna"}',
        fuente='inspeccion',
        gravedad='moderada',
        estado='abierta',
        detectado_por=user,
        fecha_deteccion=inspeccion.fecha_inspeccion,
        centro_trabajo=inspeccion.centro_trabajo,
        creado_por=user,
        fecha_limite_resolucion=inspeccion.fecha_inspeccion,
    )
    item.no_conformidad = nc
    item.save(update_fields=['no_conformidad'])
    return nc


def calcular_estadisticas_inspecciones(empresa=None):
    qs = Inspeccion.objects.all()
    if empresa:
        qs = qs.filter(empresa=empresa)

    total = qs.count()
    completadas = qs.filter(estado='completada').count()
    con_nc = qs.filter(estado='con_nc').count()
    planificadas = qs.filter(estado='planificada').count()

    return {
        'insp_total': total,
        'insp_completadas': completadas,
        'insp_con_nc': con_nc,
        'insp_planificadas': planificadas,
        'porcentaje_cumplimiento': (
            f'{round((completadas / total) * 100)}%' if total else '0%'
        ),
    }
