from django.contrib import admin
from .models import ItemPlanificacion


@admin.register(ItemPlanificacion)
class ItemPlanificacionAdmin(admin.ModelAdmin):
    list_display = [
        'ambito_puesto', 'tipo_factor_riesgo', 'factor_riesgo',
        'riesgos', 'pb', 'sv', 'gr', 'estado', 'responsable', 'fecha_objetivo',
    ]
    list_filter = ['estado', 'tipo_factor_riesgo', 'empresa']
    search_fields = ['factor_riesgo', 'ambito_puesto', 'responsable']
    raw_id_fields = ['empresa', 'evaluacion_riesgos']
