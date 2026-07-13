from django.contrib import admin
from .models import PlantillaInspeccion, PlantillaInspeccionItem, Inspeccion, ItemInspeccion


class PlantillaInspeccionItemInline(admin.TabularInline):
    model = PlantillaInspeccionItem
    extra = 1
    fields = ['orden', 'descripcion']


@admin.register(PlantillaInspeccion)
class PlantillaInspeccionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'empresa', 'categoria', 'activa']
    list_filter = ['categoria', 'activa', 'empresa']
    search_fields = ['nombre', 'descripcion', 'empresa__legal_name']
    inlines = [PlantillaInspeccionItemInline]


class ItemInspeccionInline(admin.TabularInline):
    model = ItemInspeccion
    extra = 0
    fields = ['orden', 'descripcion', 'resultado', 'observaciones']
    readonly_fields = ['no_conformidad']


@admin.register(Inspeccion)
class InspeccionAdmin(admin.ModelAdmin):
    list_display = ['id', 'empresa', 'centro_trabajo', 'inspector', 'fecha_inspeccion', 'estado', 'resultado_general']
    list_filter = ['estado', 'resultado_general', 'empresa']
    search_fields = ['centro_trabajo__name', 'observaciones', 'empresa__legal_name']
    readonly_fields = ['created_at', 'updated_at', 'nc_generadas']
    raw_id_fields = ['empresa', 'plantilla', 'centro_trabajo', 'inspector', 'creado_por']
    inlines = [ItemInspeccionInline]


@admin.register(ItemInspeccion)
class ItemInspeccionAdmin(admin.ModelAdmin):
    list_display = ['orden', 'inspeccion', 'descripcion', 'resultado']
    list_filter = ['resultado']
    search_fields = ['descripcion', 'observaciones']
    raw_id_fields = ['inspeccion', 'no_conformidad']
