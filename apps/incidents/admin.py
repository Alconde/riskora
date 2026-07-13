from django.contrib import admin
from .models import Accidente, InvestigacionAccidente, CausaAccidente, Incidente


@admin.register(CausaAccidente)
class CausaAccidenteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'empresa', 'activa']
    list_filter = ['categoria', 'activa', 'empresa']
    search_fields = ['nombre']


@admin.register(Accidente)
class AccidenteAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'titulo', 'empresa', 'centro_trabajo', 'fecha', 'tipo', 'gravedad', 'estado']
    list_filter = ['estado', 'gravedad', 'tipo', 'empresa']
    search_fields = ['codigo', 'titulo', 'descripcion', 'empresa__legal_name']
    readonly_fields = ['created_at', 'updated_at', 'nc_generada']
    raw_id_fields = ['empresa', 'centro_trabajo', 'trabajador_afectado', 'creado_por']
    filter_horizontal = ['causas']


@admin.register(InvestigacionAccidente)
class InvestigacionAccidenteAdmin(admin.ModelAdmin):
    list_display = ['accidente', 'metodologia', 'estado', 'investigador', 'fecha_inicio']
    list_filter = ['estado', 'metodologia']
    raw_id_fields = ['accidente', 'investigador']


@admin.register(Incidente)
class IncidenteAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'titulo', 'empresa', 'centro_trabajo', 'fecha', 'gravedad_potencial', 'estado']
    list_filter = ['estado', 'gravedad_potencial', 'empresa']
    search_fields = ['codigo', 'titulo', 'descripcion', 'empresa__legal_name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['empresa', 'centro_trabajo', 'trabajador_reports', 'creado_por']
