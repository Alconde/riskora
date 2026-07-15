from django.contrib import admin
from .models import MedidaPreventivaCatalogo, ItemPlanificacion


@admin.register(MedidaPreventivaCatalogo)
class MedidaPreventivaCatalogoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'frecuencia_por_defecto', 'normativa', 'activo', 'company']
    list_filter = ['categoria', 'activo', 'company']
    search_fields = ['nombre', 'normativa', 'descripcion']
    list_editable = ['activo']
    fieldsets = [
        (None, {'fields': ['nombre', 'categoria', 'activo']}),
        ('Detalles', {'fields': ['frecuencia_por_defecto', 'normativa', 'descripcion']}),
        ('Empresa (vacío = catálogo global)', {'fields': ['company']}),
    ]


@admin.register(ItemPlanificacion)
class ItemPlanificacionAdmin(admin.ModelAdmin):
    list_display = [
        'ambito_puesto', 'tipo_factor_riesgo', 'factor_riesgo',
        'riesgos', 'pb', 'sv', 'gr', 'estado', 'responsable', 'fecha_objetivo',
    ]
    list_filter = ['estado', 'tipo_factor_riesgo', 'empresa']
    search_fields = ['factor_riesgo', 'ambito_puesto', 'responsable']
    raw_id_fields = ['empresa', 'evaluacion_riesgos']
    filter_horizontal = ['medidas_catalogo']
