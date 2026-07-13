from django import forms
from .models import PlanPrevention


class PoliticaForm(forms.ModelForm):
    class Meta:
        model = PlanPrevention
        fields = ['politica', 'politica_firmada']
        widgets = {
            'politica': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        }


class OrganigramaForm(forms.ModelForm):
    class Meta:
        model = PlanPrevention
        fields = ['organigrama', 'organigrama_texto']
        widgets = {
            'organigrama': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf,.png,.jpg,.jpeg'}),
            'organigrama_texto': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }


class DelegadoPRLForm(forms.ModelForm):
    class Meta:
        model = PlanPrevention
        fields = [
            'delegado_prl', 'delegado_fecha_designacion', 'delegado_formacion',
            'doc_designacion_delegado', 'doc_formacion_delegado',
        ]
        widgets = {
            'delegado_prl': forms.Select(attrs={'class': 'form-control'}),
            'delegado_fecha_designacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'doc_designacion_delegado': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
            'doc_formacion_delegado': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        }


class RecursoPreventivoForm(forms.ModelForm):
    class Meta:
        model = PlanPrevention
        fields = [
            'recurso_preventivo', 'recurso_actividades', 'recurso_fecha_designacion',
            'recurso_formacion', 'doc_designacion_recurso', 'doc_formacion_recurso',
        ]
        widgets = {
            'recurso_preventivo': forms.Select(attrs={'class': 'form-control'}),
            'recurso_actividades': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'recurso_fecha_designacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'doc_designacion_recurso': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
            'doc_formacion_recurso': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        }


class FuncionesForm(forms.ModelForm):
    class Meta:
        model = PlanPrevention
        fields = ['funciones_responsabilidades']
        widgets = {
            'funciones_responsabilidades': forms.Textarea(attrs={'class': 'form-control', 'rows': 12}),
        }


class ETTTeletrabajoForm(forms.ModelForm):
    class Meta:
        model = PlanPrevention
        fields = ['utiliza_ett', 'puestos_ett', 'tiene_teletrabajo', 'puestos_teletrabajo']
        widgets = {
            'puestos_ett': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'puestos_teletrabajo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
