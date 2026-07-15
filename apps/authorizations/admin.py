from django.contrib import admin
from .models import RequisitoAutorizacion, AutorizacionTrabajador


@admin.register(RequisitoAutorizacion)
class RequisitoAutorizacionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'categoria', 'normativa', 'activo', 'empresa']
    list_filter = ['tipo', 'activo', 'empresa']
    search_fields = ['nombre', 'normativa']
    list_editable = ['activo']


@admin.register(AutorizacionTrabajador)
class AutorizacionTrabajadorAdmin(admin.ModelAdmin):
    list_display = [
        'trabajador', 'requisito', 'fecha_autorizacion', 'fecha_caducidad',
        'entidad_emisora', 'numero_certificado', 'activa',
    ]
    list_filter = ['activa', 'requisito__tipo', 'empresa']
    search_fields = [
        'trabajador__first_name', 'trabajador__last_name',
        'requisito__nombre', 'numero_certificado',
    ]
    raw_id_fields = ['trabajador', 'requisito']
    date_hierarchy = 'fecha_autorizacion'
