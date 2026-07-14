from django.contrib import admin
from .models import NormativaLegal, RequisitoLegal, CumplimientoLegal, AlertaLegal


class RequisitoLegalInline(admin.TabularInline):
    model = RequisitoLegal
    extra = 1


@admin.register(NormativaLegal)
class NormativaLegalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'numero', 'ambito', 'activa', 'fecha_publicacion')
    list_filter = ('tipo', 'ambito', 'activa')
    search_fields = ('nombre', 'numero')
    inlines = [RequisitoLegalInline]


@admin.register(RequisitoLegal)
class RequisitoLegalAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'normativa', 'categoria', 'articulo')
    list_filter = ('categoria',)


@admin.register(CumplimientoLegal)
class CumplimientoLegalAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'requisito', 'estado', 'fecha_evaluacion', 'fecha_proxima_revision')
    list_filter = ('estado',)
    search_fields = ('empresa__name',)
    raw_id_fields = ('requisito', 'evaluado_por', 'responsable', 'nc_generada')


@admin.register(AlertaLegal)
class AlertaLegalAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'empresa', 'leida', 'resuelta', 'fecha_creacion')
    list_filter = ('tipo', 'leida', 'resuelta')
    search_fields = ('titulo',)
