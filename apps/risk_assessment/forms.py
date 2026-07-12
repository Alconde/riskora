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
            'factor_riesgo_condicion',
            'riesgo',
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
            'factor_riesgo_condicion': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ej: Ruido elevado en zona de soldadura'}
            ),
            'riesgo': forms.Select(attrs={'class': 'form-control'}),
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
            from apps.accounts.models import User
            self.fields['puesto_trabajo'].queryset = JobPosition.objects.filter(
                company=empresa
            )
            user_ids = empresa.memberships.filter(
                is_active=True
            ).values_list('user_id', flat=True)
            self.fields['responsable_medida'].queryset = User.objects.filter(
                id__in=user_ids
            )
        self.fields['tipo_peligro'].queryset = TipoPeligro.objects.filter(activo=True)
