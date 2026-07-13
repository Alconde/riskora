from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='epis.EntregaEPI')
def entrega_post_save(sender, instance, **kwargs):
    from .models import EPI

    if instance.estado == 'activo':
        EPI.objects.filter(pk=instance.epi_id).update(estado='asignado')
    else:
        epi = instance.epi
        if not epi.entregas.filter(estado='activo').exists():
            EPI.objects.filter(pk=epi.pk, estado='asignado').update(estado='disponible')
