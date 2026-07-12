from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from .models import NoConformidad, AccionCorrectiva, AccionPreventiva


@admin.register(NoConformidad)
class NoConformidadAdmin(admin.ModelAdmin):
    list_display = [
        'codigo', 'titulo', 'empresa', 'fuente', 'gravedad',
        'estado', 'fecha_deteccion', 'fecha_limite_resolucion',
    ]
    list_filter = ['estado', 'gravedad', 'fuente', 'empresa']
    search_fields = ['codigo', 'titulo', 'descripcion', 'empresa__legal_name']
    readonly_fields = ['codigo', 'created_at', 'updated_at']
    raw_id_fields = ['empresa', 'detectado_por', 'centro_trabajo', 'trabajador', 'verificada_por', 'creado_por']


@admin.register(AccionCorrectiva)
class AccionCorrectivaAdmin(admin.ModelAdmin):
    list_display = ['id', 'no_conformidad', 'responsable', 'fecha_limite', 'estado']
    list_filter = ['estado']
    search_fields = ['descripcion', 'no_conformidad__codigo']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['no_conformidad', 'responsable']


@admin.register(AccionPreventiva)
class AccionPreventivaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'empresa', 'responsable', 'fecha_limite', 'estado']
    list_filter = ['estado', 'empresa']
    search_fields = ['titulo', 'descripcion', 'empresa__legal_name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['empresa', 'responsable', 'no_conformidad_origen']
