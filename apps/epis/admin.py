from django.contrib import admin
from .models import CatalogoEPI, EPI, EntregaEPI, InspeccionEPI


@admin.register(CatalogoEPI)
class CatalogoEPIAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'norma_eu', 'activo']
    list_filter = ['categoria', 'activo']
    search_fields = ['nombre', 'riesgos_proteccion', 'norma_eu']


@admin.register(EPI)
class EPIAdmin(admin.ModelAdmin):
    list_display = ['marca', 'modelo', 'catalogo', 'empresa', 'estado', 'fecha_compra']
    list_filter = ['estado', 'catalogo', 'empresa']
    search_fields = ['marca', 'modelo', 'numero_serie', 'empresa__legal_name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['empresa', 'catalogo']


@admin.register(EntregaEPI)
class EntregaEPIAdmin(admin.ModelAdmin):
    list_display = ['epi', 'trabajador', 'empresa', 'fecha_entrega', 'fecha_caducidad', 'estado']
    list_filter = ['estado', 'empresa']
    search_fields = ['epi__marca', 'epi__modelo', 'trabajador__first_name', 'trabajador__last_name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['empresa', 'epi', 'trabajador', 'entregado_por']


@admin.register(InspeccionEPI)
class InspeccionEPIAdmin(admin.ModelAdmin):
    list_display = ['epi', 'fecha', 'resultado', 'empresa', 'inspeccionado_por']
    list_filter = ['resultado', 'empresa']
    search_fields = ['epi__marca', 'epi__modelo', 'observaciones']
    readonly_fields = ['created_at']
    raw_id_fields = ['empresa', 'epi', 'entrega', 'inspeccionado_por']
