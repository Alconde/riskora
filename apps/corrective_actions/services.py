from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings


def generar_codigo_nc(empresa):
    year = timezone.localdate().year
    count = (
        NoConformidad.objects.filter(empresa=empresa, fecha_deteccion__year=year).count() + 1
    )
    return f'NC-{year}-{count:03d}'


def crear_alerta_nc(nc):
    from apps.tasks.models import Alert

    if nc.estado in (NoConformidad.Estado.ABIERTA, NoConformidad.Estado.EN_INVESTIGACION):
        Alert.objects.update_or_create(
            company=nc.empresa,
            title=f'NC abierta: {nc.codigo} - {nc.titulo}',
            defaults={
                'message': f'La no conformidad {nc.codigo} esta abierta. Fecha limite: {nc.fecha_limite_resolucion}.',
                'alert_type': Alert.AlertType.GENERIC,
                'severity': Alert.Severity.DANGER if nc.gravedad == 'critica' else Alert.Severity.WARNING,
                'due_date': nc.fecha_limite_resolucion,
                'is_active': True,
            },
        )


def crear_alerta_accion_correctiva(accion):
    from apps.tasks.models import Alert

    Alert.objects.create(
        company=accion.no_conformidad.empresa,
        title=f'Accion correctiva asignada: {accion.descripcion[:80]}',
        message=f'Responsable: {accion.responsable}. Fecha limite: {accion.fecha_limite}.',
        alert_type=Alert.AlertType.GENERIC,
        severity=Alert.Severity.WARNING,
        due_date=accion.fecha_limite,
        is_active=True,
    )


def notificar_vencimiento_nc(nc):
    from apps.tasks.models import Alert

    alert, created = Alert.objects.get_or_create(
        company=nc.empresa,
        title=f'NC vencida: {nc.codigo} - {nc.titulo}',
        defaults={
            'message': f'La NC {nc.codigo} ha superado su fecha limite ({nc.fecha_limite_resolucion}).',
            'alert_type': Alert.AlertType.GENERIC,
            'severity': Alert.Severity.DANGER,
            'due_date': nc.fecha_limite_resolucion,
            'is_active': True,
        },
    )
    return created


def calcular_estadisticas_nc(empresa=None):
    from .models import NoConformidad, AccionCorrectiva

    qs = NoConformidad.objects.all()
    if empresa:
        qs = qs.filter(empresa=empresa)

    today = timezone.localdate()

    total = qs.count()
    abiertas = qs.filter(estado__in=['abierta', 'en_investigacion']).count()
    en_tratamiento = qs.filter(estado='en_tratamiento').count()
    resueltas = qs.filter(estado__in=['resuelta', 'cerrada']).count()
    vencidas = qs.filter(
        estado__in=['abierta', 'en_investigacion', 'en_tratamiento'],
        fecha_limite_resolucion__lt=today,
    ).count()

    ac_qs = AccionCorrectiva.objects.filter(no_conformidad__empresa=empresa) if empresa else AccionCorrectiva.objects.all()
    ac_total = ac_qs.count()
    ac_pendientes = ac_qs.filter(estado__in=['pendiente', 'en_progreso']).count()
    ac_vencidas = ac_qs.filter(
        estado__in=['pendiente', 'en_progreso'], fecha_limite__lt=today
    ).count()

    return {
        'nc_total': total,
        'nc_abiertas': abiertas,
        'nc_en_tratamiento': en_tratamiento,
        'nc_resueltas': resueltas,
        'nc_vencidas': vencidas,
        'ac_total': ac_total,
        'ac_pendientes': ac_pendientes,
        'ac_vencidas': ac_vencidas,
        'porcentaje_resolucion': (
            f'{round((resueltas / total) * 100)}%' if total else '0%'
        ),
    }


from .models import NoConformidad
