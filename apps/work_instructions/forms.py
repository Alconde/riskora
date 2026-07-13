from django import forms
from .models import InstruccionTrabajo


class InstruccionTrabajoForm(forms.ModelForm):
    class Meta:
        model = InstruccionTrabajo
        fields = ['titulo', 'codigo', 'puesto_trabajo', 'contenido', 'file', 'revision', 'activo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'puesto_trabajo': forms.Select(attrs={'class': 'form-control'}),
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'revision': forms.NumberInput(attrs={'class': 'form-control'}),
        }
