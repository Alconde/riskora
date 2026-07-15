from django.db.models import Q
from django.utils import timezone
from datetime import timedelta


def calcular_estadisticas_autorizaciones(empresa):
    from .models import AutorizacionTrabajador

    hoy = timezone.now().date()
    limite_30 = hoy + timedelta(days=30)

    qs = AutorizacionTrabajador.objects.filter(empresa=empresa)

    total = qs.filter(activa=True).count()
    caducadas = qs.filter(
        activa=True, fecha_caducidad__lt=hoy,
    ).count()
    proximas = qs.filter(
        activa=True,
        fecha_caducidad__gte=hoy,
        fecha_caducidad__lte=limite_30,
    ).count()
    validas = total - caducadas - proximas

    return {
        'total': total,
        'validas': validas,
        'proximas_caducar': proximas,
        'caducadas': caducadas,
    }
