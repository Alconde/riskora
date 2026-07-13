from django import forms
from django.contrib.auth import get_user_model

from .models import TipoEquipo, EquipoTrabajo, RevisionEquipo, MantenimientoEquipo

User = get_user_model()


class TipoEquipoForm(forms.ModelForm):
    class Meta:
        model = TipoEquipo
        fields = ['nombre', 'categoria', 'descripcion', 'imagen', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class EquipoTrabajoForm(forms.ModelForm):
    class Meta:
        model = EquipoTrabajo
        fields = [
            'tipo', 'nombre', 'marca', 'modelo', 'numero_serie', 'numero_bien',
            'fecha_compra', 'fecha_puesta_marcha', 'ubicacion', 'responsable',
            'vida_util_meses', 'estado', 'notas',
            'manual_instrucciones', 'declaracion_ce', 'certificado_instalacion',
            'activo',
        ]
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_serie': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_bien': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_compra': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_puesta_marcha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'responsable': forms.Select(attrs={'class': 'form-control'}),
            'vida_util_meses': forms.NumberInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'manual_instrucciones': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
            'declaracion_ce': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
            'certificado_instalacion': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].queryset = TipoEquipo.objects.filter(activo=True)
        if empresa:
            self.fields['responsable'].queryset = User.objects.filter(
                companymembership__company=empresa,
                companymembership__is_active=True,
            )


class RevisionEquipoForm(forms.ModelForm):
    class Meta:
        model = RevisionEquipo
        fields = [
            'equipo', 'fecha', 'resultado', 'proxima_revision',
            'realizado_por', 'observaciones',
        ]
        widgets = {
            'equipo': forms.Select(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'resultado': forms.Select(attrs={'class': 'form-control'}),
            'proxima_revision': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'realizado_por': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields['equipo'].queryset = EquipoTrabajo.objects.filter(
                empresa=empresa, activo=True
            )
            self.fields['realizado_por'].queryset = User.objects.filter(
                companymembership__company=empresa,
                companymembership__is_active=True,
            )


class MantenimientoEquipoForm(forms.ModelForm):
    class Meta:
        model = MantenimientoEquipo
        fields = [
            'equipo', 'fecha', 'tipo', 'descripcion', 'costo',
            'realizado_por', 'proveedor',
        ]
        widgets = {
            'equipo': forms.Select(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'costo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'realizado_por': forms.Select(attrs={'class': 'form-control'}),
            'proveedor': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields['equipo'].queryset = EquipoTrabajo.objects.filter(
                empresa=empresa, activo=True
            )
            self.fields['realizado_por'].queryset = User.objects.filter(
                companymembership__company=empresa,
                companymembership__is_active=True,
            )
