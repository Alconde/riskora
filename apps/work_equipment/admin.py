from django.contrib import admin
from .models import TipoEquipo, EquipoTrabajo, RevisionEquipo, MantenimientoEquipo


@admin.register(TipoEquipo)
class TipoEquipoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'empresa', 'activo']
    list_filter = ['categoria', 'activo', 'empresa']
    search_fields = ['nombre', 'descripcion']


@admin.register(EquipoTrabajo)
class EquipoTrabajoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'marca', 'modelo', 'empresa', 'estado']
    list_filter = ['estado', 'tipo', 'empresa']
    search_fields = ['nombre', 'marca', 'modelo', 'numero_serie']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['empresa', 'tipo', 'responsable']


@admin.register(RevisionEquipo)
class RevisionEquipoAdmin(admin.ModelAdmin):
    list_display = ['equipo', 'fecha', 'resultado', 'proxima_revision', 'empresa']
    list_filter = ['resultado', 'empresa']
    search_fields = ['equipo__nombre', 'observaciones']
    readonly_fields = ['created_at']
    raw_id_fields = ['empresa', 'equipo', 'realizado_por']


@admin.register(MantenimientoEquipo)
class MantenimientoEquipoAdmin(admin.ModelAdmin):
    list_display = ['equipo', 'fecha', 'tipo', 'costo', 'proveedor', 'empresa']
    list_filter = ['tipo', 'empresa']
    search_fields = ['equipo__nombre', 'descripcion', 'proveedor']
    readonly_fields = ['created_at']
    raw_id_fields = ['empresa', 'equipo', 'realizado_por']
