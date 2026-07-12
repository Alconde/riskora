from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import NoConformidad, AccionCorrectiva
from .services import crear_alerta_nc, crear_alerta_accion_correctiva


@receiver(post_save, sender=NoConformidad)
def nc_post_save(sender, instance, created, **kwargs):
    crear_alerta_nc(instance)


@receiver(post_save, sender=AccionCorrectiva)
def ac_post_save(sender, instance, created, **kwargs):
    if created and instance.responsable:
        crear_alerta_accion_correctiva(instance)
