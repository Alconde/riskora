from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='epps.EnfermedadProfesional')
def epp_post_save(sender, instance, created, **kwargs):
    if created and instance.estado == 'abierto':
        from apps.tasks.models import Alert
        if instance.gravedad in ('grave', 'muy_grave'):
            Alert.objects.create(
                company=instance.empresa,
                title=f'EEPP grave: {instance.codigo} - {instance.titulo}',
                message=(
                    f'Enfermedad profesional con gravedad '
                    f'"{instance.get_gravedad_display()}". '
                    f'Centro: {instance.centro_trabajo}. '
                    f'Fecha diagnostico: {instance.fecha_diagnostico}.'
                ),
                alert_type=Alert.AlertType.GENERIC,
                severity=Alert.Severity.DANGER,
                is_active=True,
            )
