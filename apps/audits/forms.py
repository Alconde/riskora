from django import forms
from .models import (
    ProgramaAuditoria,
    AuditoriaInterna,
    ChecklistAuditoria,
    InformeAuditoria,
)


class ProgramaAuditoriaForm(forms.ModelForm):
    class Meta:
        model = ProgramaAuditoria
        fields = ['anio', 'version', 'alcance', 'notas']
        widgets = {
            'anio': forms.NumberInput(attrs={'class': 'form-control', 'min': 2020, 'max': 2100}),
            'version': forms.TextInput(attrs={'class': 'form-control'}),
            'alcance': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class AuditoriaInternaForm(forms.ModelForm):
    class Meta:
        model = AuditoriaInterna
        fields = [
            'programa', 'titulo', 'descripcion', 'fecha_planificada',
            'lider_auditoria', 'auditados', 'observaciones',
        ]
        widgets = {
            'programa': forms.Select(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha_planificada': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'lider_auditoria': forms.Select(attrs={'class': 'form-control'}),
            'auditados': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class ChecklistAuditoriaForm(forms.ModelForm):
    class Meta:
        model = ChecklistAuditoria
        fields = [
            'clausula_iso', 'seccion', 'requisito', 'evidencia_requerida',
            'conformidad', 'hallazgo', 'evidencia_encontrada',
            'responsable_seguimiento', 'plazo_cierre', 'cerrado',
        ]
        widgets = {
            'clausula_iso': forms.TextInput(attrs={'class': 'form-control'}),
            'seccion': forms.TextInput(attrs={'class': 'form-control'}),
            'requisito': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'evidencia_requerida': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'conformidad': forms.Select(attrs={'class': 'form-control'}),
            'hallazgo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'evidencia_encontrada': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'responsable_seguimiento': forms.Select(attrs={'class': 'form-control'}),
            'plazo_cierre': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cerrado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ChecklistBulkForm(forms.Form):
    """Formulario para carga múltiple de items de checklist desde ISO 45001."""
    clausulas = forms.MultipleChoiceField(
        label='Seleccionar cláusulas ISO 45001',
        choices=[],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True,
    )

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.audits.services import get_checklist_plantilla
        plantilla = get_checklist_plantilla(empresa)
        self.fields['clausulas'].choices = [
            (item['id'], f"{item['clausula']} — {item['requisito'][:80]}")
            for item in plantilla
        ]


class InformeAuditoriaForm(forms.ModelForm):
    class Meta:
        model = InformeAuditoria
        fields = [
            'resumen_ejecutivo', 'hallazgos_resumen', 'puntos_fuertes',
            'oportunidades_mejora', 'recomendaciones', 'fecha_informe',
            'elaborado_por', 'aprobado_por',
        ]
        widgets = {
            'resumen_ejecutivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'hallazgos_resumen': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'puntos_fuertes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'oportunidades_mejora': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recomendaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha_informe': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'elaborado_por': forms.Select(attrs={'class': 'form-control'}),
            'aprobado_por': forms.Select(attrs={'class': 'form-control'}),
        }
