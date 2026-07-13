from django.db import models


def generar_codigo_accidente(empresa):
    from django.utils import timezone
    year = timezone.localdate().year
    from .models import Accidente
    count = (
        Accidente.objects.filter(empresa=empresa, fecha__year=year).count() + 1
    )
    return f'ACC-{year}-{count:03d}'


def generar_codigo_incidente(empresa):
    from django.utils import timezone
    year = timezone.localdate().year
    from .models import Incidente
    count = (
        Incidente.objects.filter(empresa=empresa, fecha__year=year).count() + 1
    )
    return f'INC-{year}-{count:03d}'


def generar_nc_desde_accidente(accidente, user, form_data=None):
    from apps.corrective_actions.models import NoConformidad
    from apps.corrective_actions.services import generar_codigo_nc

    titulo = (form_data or {}).get('titulo') or f'NC desde accidente {accidente.codigo}: {accidente.titulo}'
    descripcion = (form_data or {}).get('descripcion') or (
        f'Accidente de trabajo:\n\n'
        f'{accidente.descripcion}\n\n'
        f'Tipo: {accidente.get_tipo_display()}\n'
        f'Gravedad: {accidente.get_gravedad_display()}\n'
        f'Lesion: {accidente.get_tipo_lesion_display()}\n'
        f'Parte del cuerpo: {accidente.parte_cuerpo or "No especificada"}'
    )
    gravedad = (form_data or {}).get('gravedad') or _mapear_gravedad_nc(accidente.gravedad)
    fecha_limite = (form_data or {}).get('fecha_limite_resolucion') or accidente.fecha.date()

    nc = NoConformidad.objects.create(
        empresa=accidente.empresa,
        codigo=generar_codigo_nc(accidente.empresa),
        titulo=titulo,
        descripcion=descripcion,
        fuente='accidente',
        gravedad=gravedad,
        estado='en_investigacion',
        detectado_por=user,
        fecha_deteccion=accidente.fecha.date(),
        centro_trabajo=accidente.centro_trabajo,
        trabajador=accidente.trabajador_afectado,
        ubicacion=accidente.ubicacion,
        creado_por=user,
        fecha_limite_resolucion=fecha_limite,
    )
    accidente.nc_generada = nc
    accidente.save(update_fields=['nc_generada'])
    return nc


def _mapear_gravedad_nc(gravedad_accidente):
    mapping = {
        'sin_baja': 'menor',
        'baja_temporal': 'moderada',
        'baja_permanente': 'importante',
        'mortal': 'critica',
    }
    return mapping.get(gravedad_accidente, 'moderada')


def calcular_estadisticas_accidentes(empresa=None):
    from .models import Accidente, Incidente

    acc_qs = Accidente.objects.all()
    inc_qs = Incidente.objects.all()
    if empresa:
        acc_qs = acc_qs.filter(empresa=empresa)
        inc_qs = inc_qs.filter(empresa=empresa)

    total_acc = acc_qs.count()
    abiertos = acc_qs.filter(estado='abierto').count()
    en_investigacion = acc_qs.filter(estado='en_investigacion').count()
    cerrados = acc_qs.filter(estado='cerrado').count()
    mortales = acc_qs.filter(gravedad='mortal').count()
    con_baja = acc_qs.filter(
        gravedad__in=['baja_temporal', 'baja_permanente']
    ).count()

    total_inc = inc_qs.count()
    inc_abiertos = inc_qs.filter(estado='abierto').count()
    inc_cerrados = inc_qs.filter(estado='cerrado').count()

    return {
        'acc_total': total_acc,
        'acc_abiertos': abiertos,
        'acc_en_investigacion': en_investigacion,
        'acc_cerrados': cerrados,
        'acc_mortales': mortales,
        'acc_con_baja': con_baja,
        'inc_total': total_inc,
        'inc_abiertos': inc_abiertos,
        'inc_cerrados': inc_cerrados,
        'tasa_cierre': (
            f'{round((cerrados / total_acc) * 100)}%' if total_acc else '0%'
        ),
    }
