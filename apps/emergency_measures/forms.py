from django import forms
from .models import (
    PlanAutoproteccion, EmpresaMedioProteccion, EquipoEmergencia,
    MiembroEquipoEmergencia, RegistroSimulacro, EntregaInformacionEmergencia
)


class PlanAutoproteccionForm(forms.ModelForm):
    class Meta:
        model = PlanAutoproteccion
        fields = ['file_plan', 'file_plano', 'notas_plano', 'fecha_revision', 'proxima_revision']
        widgets = {
            'notas_plano': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha_revision': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'proxima_revision': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class EmpresaMedioProteccionForm(forms.ModelForm):
    class Meta:
        model = EmpresaMedioProteccion
        fields = ['medio', 'cantidad', 'ubicacion', 'notas']
        widgets = {
            'medio': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class EquipoEmergenciaForm(forms.ModelForm):
    class Meta:
        model = EquipoEmergencia
        fields = ['tipo', 'nombre', 'designacion_file', 'formacion_file', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class MiembroEquipoForm(forms.ModelForm):
    class Meta:
        model = MiembroEquipoEmergencia
        fields = ['trabajador', 'rol', 'designacion_file', 'formacion_file']
        widgets = {
            'trabajador': forms.Select(attrs={'class': 'form-control'}),
            'rol': forms.TextInput(attrs={'class': 'form-control'}),
        }


class RegistroSimulacroForm(forms.ModelForm):
    class Meta:
        model = RegistroSimulacro
        fields = ['fecha', 'descripcion', 'participantes', 'duracion_minutos', 'observaciones', 'archivo']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'participantes': forms.NumberInput(attrs={'class': 'form-control'}),
            'duracion_minutos': forms.NumberInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class EntregaInformacionForm(forms.ModelForm):
    class Meta:
        model = EntregaInformacionEmergencia
        fields = ['trabajador', 'fecha_entrega', 'tipo_informacion', 'descripcion',
                  'firma_trabajador', 'archivo', 'notas']
        widgets = {
            'trabajador': forms.Select(attrs={'class': 'form-control'}),
            'fecha_entrega': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tipo_informacion': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
