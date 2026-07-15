from django.contrib import admin
from .models import PlanPrevention


@admin.register(PlanPrevention)
class PlanPreventionAdmin(admin.ModelAdmin):
    list_display = (
        'company', 'politica_firmada', 'delegado_prl',
        'recurso_preventivo', 'utiliza_ett', 'tiene_teletrabajo',
        'created_at',
    )
    list_filter = ('politica_firmada', 'delegado_prl', 'recurso_preventivo')
    search_fields = ('company__name',)
    readonly_fields = ('created_at', 'updated_at')
