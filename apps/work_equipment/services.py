from django.db import models


def calcular_estadisticas_equipos(empresa=None):
    from .models import EquipoTrabajo, RevisionEquipo, MantenimientoEquipo
    from django.utils import timezone

    eq_qs = EquipoTrabajo.objects.all()
    rev_qs = RevisionEquipo.objects.all()
    mant_qs = MantenimientoEquipo.objects.all()
    if empresa:
        eq_qs = eq_qs.filter(empresa=empresa)
        rev_qs = rev_qs.filter(empresa=empresa)
        mant_qs = mant_qs.filter(empresa=empresa)

    total = eq_qs.count()
    operativos = eq_qs.filter(estado='operativo').count()
    en_mant = eq_qs.filter(estado='en_mantenimiento').count()
    retirados = eq_qs.filter(estado='retirado').count()
    bajas = eq_qs.filter(estado='baja').count()

    hoy = timezone.localdate()
    revisiones_pendientes = sum(
        1 for eq in eq_qs.filter(activo=True)
        if eq.revision_pendiente
    )

    total_revisiones = rev_qs.count()
    rev_no_conforme = rev_qs.filter(resultado__in=['no_conforme', 'observaciones']).count()

    total_mant = mant_qs.count()
    coste_total = mant_qs.aggregate(total=models.Sum('costo'))['total'] or 0

    return {
        'eq_total': total,
        'eq_operativos': operativos,
        'eq_en_mantenimiento': en_mant,
        'eq_retirados': retirados,
        'eq_bajas': bajas,
        'eq_revisiones_pendientes': revisiones_pendientes,
        'rev_total': total_revisiones,
        'rev_no_conforme': rev_no_conforme,
        'mant_total': total_mant,
        'mant_coste_total': coste_total,
    }
