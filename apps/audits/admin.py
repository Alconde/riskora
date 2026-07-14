from django.contrib import admin
from .models import (
    ProgramaAuditoria,
    AuditoriaInterna,
    ChecklistAuditoria,
    InformeAuditoria,
)


@admin.register(ProgramaAuditoria)
class ProgramaAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'anio', 'version', 'estado', 'aprobado_por', 'fecha_aprobacion')
    list_filter = ('estado', 'anio')
    search_fields = ('empresa__name',)


@admin.register(AuditoriaInterna)
class AuditoriaInternaAdmin(admin.ModelAdmin):
    list_display = ('pk', 'titulo', 'empresa', 'programa', 'fecha_planificada', 'estado')
    list_filter = ('estado', 'empresa')
    search_fields = ('titulo',)
    raw_id_fields = ('programa', 'lider_auditoria')


@admin.register(ChecklistAuditoria)
class ChecklistAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('auditoria', 'clausula_iso', 'seccion', 'conformidad', 'cerrado')
    list_filter = ('conformidad', 'cerrado')
    search_fields = ('requisito',)
    raw_id_fields = ('auditoria',)


@admin.register(InformeAuditoria)
class InformeAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('auditoria', 'fecha_informe', 'elaborado_por', 'aprobado_por')
    list_filter = ('fecha_informe',)
    raw_id_fields = ('auditoria', 'elaborado_por', 'aprobado_por')
