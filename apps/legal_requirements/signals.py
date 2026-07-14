from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CumplimientoLegal, AlertaLegal


@receiver(post_save, sender=CumplimientoLegal)
def crear_alerta_no_cumplimiento(sender, instance, **kwargs):
    """Crea una alerta cuando un cumplimiento cambia a 'no_cumple'."""
    if instance.estado != 'no_cumple':
        return
    if AlertaLegal.objects.filter(
        empresa=instance.empresa,
        cumplimiento=instance,
        tipo='no_cumplimiento',
        resuelta=False,
    ).exists():
        return
    AlertaLegal.objects.create(
        empresa=instance.empresa,
        tipo='no_cumplimiento',
        titulo=f'No cumplimiento: {instance.requisito.titulo[:80]}',
        descripcion=(
            f'El requisito legal "{instance.requisito.titulo}" '
            f'({instance.requisito.normativa}) ha sido marcado como NO CUMPLIDO.'
        ),
        cumplimiento=instance,
        normativa=instance.requisito.normativa,
    )


@receiver(post_save, sender=CumplimientoLegal)
def crear_alerta_revision_proxima(sender, instance, **kwargs):
    """Crea una alerta cuando la próxima revisión está a menos de 30 días."""
    if not instance.fecha_proxima_revision:
        return
    from datetime import date
    hoy = date.today()
    dias = (instance.fecha_proxima_revision - hoy).days
    if dias < 0:
        titulo = f'Revisión vencida: {instance.requisito.titulo[:60]}'
        tipo = 'vencimiento'
    elif dias <= 30:
        titulo = f'Revisión en {dias} días: {instance.requisito.titulo[:60]}'
        tipo = 'vencimiento'
    else:
        return

    if AlertaLegal.objects.filter(
        empresa=instance.empresa,
        cumplimiento=instance,
        tipo=tipo,
        resuelta=False,
    ).exists():
        return

    AlertaLegal.objects.create(
        empresa=instance.empresa,
        tipo=tipo,
        titulo=titulo,
        descripcion=(
            f'La próxima revisión del cumplimiento legal de '
            f'"{instance.requisito.titulo}" está programada para el '
            f'{instance.fecha_proxima_revision.strftime("%d/%m/%Y")}.'
        ),
        cumplimiento=instance,
        normativa=instance.requisito.normativa,
    )
