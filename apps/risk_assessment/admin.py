from django.contrib import admin

from apps.risk_assessment.models import (
    TipoPeligro,
    EvaluacionRiesgos,
    ItemEvaluacionRiesgos,
    NivelRiesgoReferencia,
)


@admin.register(TipoPeligro)
class TipoPeligroAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'categoria', 'activo')
    list_filter = ('categoria', 'activo')
    search_fields = ('nombre', 'codigo')
    list_editable = ('activo',)


class ItemEvaluacionInline(admin.TabularInline):
    model = ItemEvaluacionRiesgos
    extra = 0
    readonly_fields = ('grado_riesgo', 'nivel_riesgo')
    fields = (
        'puesto_trabajo',
        'factor_riesgo_condicion',
        'riesgo',
        'tipo_peligro',
        'probabilidad',
        'severidad',
        'grado_riesgo',
        'nivel_riesgo',
        'medidas_propuestas',
        'estado_implementacion',
    )


@admin.register(EvaluacionRiesgos)
class EvaluacionRiesgosAdmin(admin.ModelAdmin):
    list_display = (
        'titulo',
        'empresa',
        'centro_trabajo',
        'fecha_evaluacion',
        'estado',
        'version',
    )
    list_filter = ('estado', 'empresa', 'metodologia')
    search_fields = ('titulo', 'centro_trabajo__name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ItemEvaluacionInline]


@admin.register(ItemEvaluacionRiesgos)
class ItemEvaluacionRiesgosAdmin(admin.ModelAdmin):
    list_display = (
        'evaluacion',
        'puesto_trabajo',
        'factor_riesgo_condicion',
        'riesgo',
        'probabilidad',
        'severidad',
        'grado_riesgo',
        'nivel_riesgo',
        'estado_implementacion',
    )
    list_filter = ('nivel_riesgo', 'estado_implementacion', 'riesgo')
    search_fields = ('factor_riesgo_condicion',)
    readonly_fields = ('grado_riesgo', 'nivel_riesgo')


@admin.register(NivelRiesgoReferencia)
class NivelRiesgoReferenciaAdmin(admin.ModelAdmin):
    list_display = ('grado', 'probabilidad', 'severidad', 'nivel', 'etiqueta', 'color')
    ordering = ('grado',)
    readonly_fields = ('grado',)
