from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.risk_assessment.models import ItemEvaluacionRiesgos
from apps.risk_assessment.services import calcular_grado_riesgo


@receiver(pre_save, sender=ItemEvaluacionRiesgos)
def calcular_riesgo_automatico(sender, instance, **kwargs):
    """Calcula automáticamente el grado de riesgo al guardar un item."""
    resultado = calcular_grado_riesgo(instance.probabilidad, instance.severidad)
    instance.grado_riesgo = resultado['grado']
    instance.nivel_riesgo = resultado['nivel']
