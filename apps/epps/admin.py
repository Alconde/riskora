from django.contrib import admin
from .models import EnfermedadProfesional, InvestigacionEEPP, ProcedimientoInvestigacionEEPP


@admin.register(EnfermedadProfesional)
class EnfermedadProfesionalAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'titulo', 'empresa', 'centro_trabajo', 'fecha_diagnostico', 'agente_causante', 'gravedad', 'estado']
    list_filter = ['estado', 'gravedad', 'agente_causante', 'empresa']
    search_fields = ['codigo', 'titulo', 'nombre_enfermedad', 'empresa__legal_name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['empresa', 'centro_trabajo', 'trabajador_afectado', 'creado_por']


@admin.register(InvestigacionEEPP)
class InvestigacionEEPPAdmin(admin.ModelAdmin):
    list_display = ['enfermedad', 'metodologia', 'estado', 'investigador', 'revisor', 'fecha_inicio']
    list_filter = ['estado', 'metodologia']
    raw_id_fields = ['enfermedad', 'investigador', 'responsable', 'revisor']


@admin.register(ProcedimientoInvestigacionEEPP)
class ProcedimientoInvestigacionEEPPAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'version', 'empresa', 'activo', 'subido_por', 'created_at']
    list_filter = ['activo', 'empresa']
    search_fields = ['titulo']
    raw_id_fields = ['empresa', 'subido_por']
