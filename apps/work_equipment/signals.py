from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='work_equipment.RevisionEquipo')
def revision_post_save(sender, instance, **kwargs):
    from .models import EquipoTrabajo

    if instance.resultado == 'no_conforme':
        EquipoTrabajo.objects.filter(
            pk=instance.equipo_id, estado='operativo'
        ).update(estado='en_mantenimiento')
