from django import forms
from .models import ItemPlanificacion


class ItemPlanificacionForm(forms.ModelForm):
    class Meta:
        model = ItemPlanificacion
        fields = [
            'evaluacion_riesgos', 'ambito_puesto', 'tipo_factor_riesgo',
            'factor_riesgo', 'detalle', 'riesgos', 'pb', 'sv', 'gr',
            'medidas_preventivas', 'detalle_medida', 'plazo_limite',
            'fecha_objetivo', 'responsable', 'costes', 'estado', 'origen',
        ]
        widgets = {
            'evaluacion_riesgos': forms.Select(attrs={'class': 'form-control'}),
            'ambito_puesto': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_factor_riesgo': forms.Select(attrs={'class': 'form-control'}),
            'factor_riesgo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'detalle': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'riesgos': forms.Select(attrs={'class': 'form-control'}),
            'pb': forms.Select(attrs={'class': 'form-control'}),
            'sv': forms.Select(attrs={'class': 'form-control'}),
            'gr': forms.Select(attrs={'class': 'form-control'}),
            'medidas_preventivas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'detalle_medida': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'plazo_limite': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_objetivo': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'responsable': forms.TextInput(attrs={'class': 'form-control'}),
            'costes': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'origen': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            from apps.risk_assessment.models import EvaluacionRiesgos
            self.fields['evaluacion_riesgos'].queryset = EvaluacionRiesgos.objects.filter(
                empresa=empresa
            )
        else:
            self.fields['evaluacion_riesgos'].required = False
