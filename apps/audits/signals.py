from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ChecklistAuditoria, AuditoriaInterna


@receiver(post_save, sender=ChecklistAuditoria)
def crear_nc_desde_no_conformidad(sender, instance, **kwargs):
    """Cuando un ítem de checklist se marca como no conforme, crea una NoConformidad."""
    if instance.conformidad != 'no_conforme':
        return
    if instance.accion_correctiva_id is not None:
        return
    if not instance.hallazgo:
        return

    from apps.corrective_actions.models import NoConformidad

    nc = NoConformidad.objects.create(
        empresa=instance.auditoria.empresa,
        titulo=f'NC auditoría AUD-{instance.auditoria.pk:04d} — {instance.clausula_iso}',
        descripcion=(
            f'No conformidad detectada en auditoría interna.\n\n'
            f'Cláusula: {instance.clausula_iso}\n'
            f'Sección: {instance.seccion}\n'
            f'Requisito: {instance.requisito}\n\n'
            f'Hallazgo:\n{instance.hallazgo}\n\n'
            f'Evidencia encontrada:\n{instance.evidencia_encontrada}'
        ),
        origen='auditoria',
        estado='abierta',
    )
    instance.accion_correctiva = nc
    instance.save(update_fields=['accion_correctiva'])


@receiver(post_save, sender=AuditoriaInterna)
def actualizar_estado_programa(sender, instance, **kwargs):
    """Actualiza el estado del programa cuando cambia el estado de una auditoría."""
    programa = instance.programa
    if programa.estado == 'borrador':
        return

    total = programa.total_auditorias
    completadas = programa.auditorias.filter(estado='completada').count()
    en_curso = programa.auditorias.filter(estado='en_curso').count()

    if completadas == total and total > 0:
        programa.estado = 'completado'
    elif en_curso > 0 or completadas > 0:
        programa.estado = 'en_ejecucion'
    else:
        return

    programa.save(update_fields=['estado'])
