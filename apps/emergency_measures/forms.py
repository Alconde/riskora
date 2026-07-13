from django import forms
from .models import MedidaEmergencia, HistorialSimulacro


class MedidaEmergenciaForm(forms.ModelForm):
    class Meta:
        model = MedidaEmergencia
        fields = ['tipo', 'titulo', 'descripcion', 'ubicacion', 'fecha',
                  'proximo_simulacro', 'responsable', 'file', 'activo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'proximo_simulacro': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class HistorialSimulacroForm(forms.ModelForm):
    class Meta:
        model = HistorialSimulacro
        fields = ['medida', 'fecha', 'participantes', 'observaciones']
        widgets = {
            'medida': forms.Select(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'participantes': forms.NumberInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
