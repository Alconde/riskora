from django.contrib import admin
from .models import (
    EmpresaSubcontrata, DocumentoCAETipo, DocumentoCAE,
    ProcedimientoCAE, CartaCAE, DocumentoRiesgosCAE,
)


@admin.register(EmpresaSubcontrata)
class EmpresaSubcontrataAdmin(admin.ModelAdmin):
    list_display = ('nombre_empresa', 'empresa', 'persona_contacto', 'activa', 'habilitada')
    list_filter = ('activa',)
    search_fields = ('nombre_empresa', 'persona_contacto')


@admin.register(DocumentoCAETipo)
class DocumentoCAETipoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'obligatorio', 'orden', 'activo')
    list_filter = ('obligatorio', 'activo')


@admin.register(DocumentoCAE)
class DocumentoCAEAdmin(admin.ModelAdmin):
    list_display = ('empresa_subcontrata', 'tipo_documento', 'subido', 'actualizado', 'fecha_caducidad')
    list_filter = ('tipo_documento',)


@admin.register(ProcedimientoCAE)
class ProcedimientoCAEAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'version', 'fecha')


@admin.register(CartaCAE)
class CartaCAEAdmin(admin.ModelAdmin):
    list_display = ('empresa',)


@admin.register(DocumentoRiesgosCAE)
class DocumentoRiesgosCAEAdmin(admin.ModelAdmin):
    list_display = ('empresa',)
