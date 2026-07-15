from django import forms
from django.db import models

from apps.authorizations.models import RequisitoAutorizacion, AutorizacionTrabajador


class RequisitoAutorizacionForm(forms.ModelForm):
    class Meta:
        model = RequisitoAutorizacion
        fields = ['nombre', 'tipo', 'categoria', 'normativa', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'categoria': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ej: Maquinaria, Trabajos especiales'}
            ),
            'normativa': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ej: RD 1215/1997'}
            ),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class AutorizacionTrabajadorForm(forms.ModelForm):
    class Meta:
        model = AutorizacionTrabajador
        fields = [
            'trabajador', 'requisito', 'fecha_autorizacion', 'fecha_caducidad',
            'entidad_emisora', 'numero_certificado', 'archivo', 'observaciones',
        ]
        widgets = {
            'trabajador': forms.Select(attrs={'class': 'form-control'}),
            'requisito': forms.Select(attrs={'class': 'form-control'}),
            'fecha_autorizacion': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'fecha_caducidad': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'entidad_emisora': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ej: INSST, AENOR'}
            ),
            'numero_certificado': forms.TextInput(attrs={'class': 'form-control'}),
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.workers.models import Worker
        if empresa:
            self.fields['trabajador'].queryset = Worker.objects.filter(
                company=empresa, employment_status='active'
            )
            self.fields['requisito'].queryset = RequisitoAutorizacion.objects.filter(
                models.Q(empresa__isnull=True) | models.Q(empresa=empresa),
                activo=True,
            )
        else:
            self.fields['trabajador'].queryset = Worker.objects.none()
            self.fields['requisito'].queryset = RequisitoAutorizacion.objects.filter(
                empresa__isnull=True, activo=True,
            )
