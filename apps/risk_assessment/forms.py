from django import forms

from apps.risk_assessment.models import (
    EvaluacionRiesgos,
    ItemEvaluacionRiesgos,
    TipoPeligro,
)


class EvaluacionRiesgosForm(forms.ModelForm):
    class Meta:
        model = EvaluacionRiesgos
        fields = [
            'empresa',
            'centro_trabajo',
            'titulo',
            'fecha_evaluacion',
            'fecha_proxima_revision',
            'metodologia',
            'revisado_por',
            'observaciones',
        ]
        widgets = {
            'empresa': forms.Select(attrs={'class': 'form-control'}),
            'centro_trabajo': forms.Select(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_evaluacion': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'fecha_proxima_revision': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'metodologia': forms.Select(attrs={'class': 'form-control'}),
            'revisado_por': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ItemEvaluacionRiesgosForm(forms.ModelForm):
    class Meta:
        model = ItemEvaluacionRiesgos
        fields = [
            'puesto_trabajo',
            'tipo_peligro',
            'descripcion_peligro',
            'medidas_existentes',
            'probabilidad',
            'severidad',
            'medidas_propuestas',
            'responsable_medida',
            'fecha_limite_implementacion',
            'estado_implementacion',
        ]
        widgets = {
            'puesto_trabajo': forms.Select(attrs={'class': 'form-control'}),
            'tipo_peligro': forms.Select(attrs={'class': 'form-control'}),
            'descripcion_peligro': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 2}
            ),
            'medidas_existentes': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 2}
            ),
            'probabilidad': forms.Select(attrs={'class': 'form-control'}),
            'severidad': forms.Select(attrs={'class': 'form-control'}),
            'medidas_propuestas': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 2}
            ),
            'responsable_medida': forms.Select(attrs={'class': 'form-control'}),
            'fecha_limite_implementacion': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'estado_implementacion': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            from apps.workers.models import JobPosition
            self.fields['puesto_trabajo'].queryset = JobPosition.objects.filter(
                empresa=empresa
            )
            self.fields['responsable_medida'].queryset = empresa.members.filter(
                is_active=True
            )
        self.fields['tipo_peligro'].queryset = TipoPeligro.objects.filter(activo=True)
