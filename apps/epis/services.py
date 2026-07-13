from django.db import models


def calcular_estadisticas_epis(empresa=None):
    from .models import EPI, EntregaEPI, InspeccionEPI
    from django.utils import timezone

    epi_qs = EPI.objects.all()
    ent_qs = EntregaEPI.objects.all()
    insp_qs = InspeccionEPI.objects.all()
    if empresa:
        epi_qs = epi_qs.filter(empresa=empresa)
        ent_qs = ent_qs.filter(empresa=empresa)
        insp_qs = insp_qs.filter(empresa=empresa)

    total_epis = epi_qs.count()
    disponibles = epi_qs.filter(estado='disponible').count()
    asignados = epi_qs.filter(estado='asignado').count()
    retirados = epi_qs.filter(estado='retirado').count()

    total_entregas = ent_qs.count()
    activas = ent_qs.filter(estado='activo').count()
    hoy = timezone.localdate()
    caducadas = ent_qs.filter(estado='activo', fecha_caducidad__lt=hoy).count()
    por_caducar = ent_qs.filter(
        estado='activo',
        fecha_caducidad__gte=hoy,
        fecha_caducidad__lte=hoy + timezone.timedelta(days=30),
    ).count()

    total_inspecciones = insp_qs.count()
    insp_malas = insp_qs.filter(resultado__in=['malo', 'rechazado']).count()

    return {
        'epi_total': total_epis,
        'epi_disponibles': disponibles,
        'epi_asignados': asignados,
        'epi_retirados': retirados,
        'ent_total': total_entregas,
        'ent_activas': activas,
        'ent_caducadas': caducadas,
        'ent_por_caducar': por_caducar,
        'insp_total': total_inspecciones,
        'insp_malas': insp_malas,
    }
