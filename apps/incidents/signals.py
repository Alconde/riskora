from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='incidents.Accidente')
def accidente_post_save(sender, instance, created, **kwargs):
    if created and instance.estado == 'abierto':
        from apps.tasks.models import Alert
        if instance.gravedad in ('baja_permanente', 'mortal'):
            Alert.objects.create(
                company=instance.empresa,
                title=f'Accidente grave: {instance.codigo} - {instance.titulo}',
                message=(
                    f'Accidente con gravedad "{instance.get_gravedad_display()}". '
                    f'Centro: {instance.centro_trabajo}. '
                    f'Fecha: {instance.fecha}.'
                ),
                alert_type=Alert.AlertType.GENERIC,
                severity=Alert.Severity.DANGER,
                is_active=True,
            )
