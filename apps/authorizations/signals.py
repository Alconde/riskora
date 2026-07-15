from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


@receiver(post_save, sender='authorizations.AutorizacionTrabajador')
def gestionar_alertas_autorizacion(sender, instance, **kwargs):
    """Al guardar una autorización, crear/cerrar tareas de renovación si caduca pronto."""
    from apps.tasks.models import Task, Alert
    from datetime import timedelta

    hoy = timezone.now().date()
    titulo_base = f'Renovar autorización: {instance.requisito.nombre} - {instance.trabajador}'

    if not instance.activa:
        Task.objects.filter(
            title=titulo_base,
            status='pending',
        ).update(status='cancelled')
        return

    if not instance.fecha_caducidad:
        return

    dias_restantes = (instance.fecha_caducidad - hoy).days

    if dias_restantes < 0:
        return

    if dias_restantes <= 30:
        existe_task = Task.objects.filter(
            title=titulo_base,
            status='pending',
        ).exists()

        if not existe_task:
            Task.objects.create(
                company=instance.empresa,
                title=titulo_base,
                description=(
                    f'La autorización de {instance.trabajador} para '
                    f'"{instance.requisito.nombre}" caduca el '
                    f'{instance.fecha_caducidad.strftime("%d/%m/%Y")}. '
                    f'Renovar antes de la fecha de caducidad.'
                ),
                priority='high' if dias_restantes <= 7 else 'medium',
                due_date=instance.fecha_caducidad,
            )

        Alert.objects.get_or_create(
            company=instance.empresa,
            title=f'Autorización próxima a caducar: {instance.requisito.nombre}',
            message=(
                f'La autorización de {instance.trabajador} para '
                f'"{instance.requisito.nombre}" caduca el '
                f'{instance.fecha_caducidad.strftime("%d/%m/%Y")}.'
            ),
            alert_type='generic',
            severity='danger' if dias_restantes <= 7 else 'warning',
            due_date=instance.fecha_caducidad,
            defaults={'is_active': True},
        )
