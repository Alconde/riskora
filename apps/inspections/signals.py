from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='inspections.ItemInspeccion')
def item_post_save(sender, instance, **kwargs):
    from .models import Inspeccion

    inspeccion = instance.inspeccion
    tiene_nc = inspeccion.items.filter(resultado='no_conforme').exists()
    if tiene_nc and inspeccion.estado != Inspeccion.Estado.CON_NC:
        inspeccion.estado = Inspeccion.Estado.CON_NC
        inspeccion.nc_generadas = True
        inspeccion.save(update_fields=['estado', 'nc_generadas', 'updated_at'])
