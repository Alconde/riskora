from django import forms
from .models import ReconocimientoMedico, ControlSalud


class ReconocimientoMedicoForm(forms.ModelForm):
    class Meta:
        model = ReconocimientoMedico
        fields = ['trabajador', 'tipo', 'fecha', 'proximo_reconocimiento',
                  'apto', 'observaciones', 'medico', 'file']
        widgets = {
            'trabajador': forms.Select(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'proximo_reconocimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medico': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ControlSaludForm(forms.ModelForm):
    class Meta:
        model = ControlSalud
        fields = ['trabajador', 'fecha', 'tipo_control', 'resultados', 'recomendaciones', 'file']
        widgets = {
            'trabajador': forms.Select(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tipo_control': forms.TextInput(attrs={'class': 'form-control'}),
            'resultados': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recomendaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
