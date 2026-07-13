from django import forms
from django.contrib.auth import get_user_model
from django.db import models

from .models import Accidente, InvestigacionAccidente, CausaAccidente, Incidente

User = get_user_model()


class AccidenteForm(forms.ModelForm):
    class Meta:
        model = Accidente
        fields = [
            'titulo', 'fecha', 'centro_trabajo', 'ubicacion',
            'tipo', 'gravedad', 'tipo_lesion', 'parte_cuerpo',
            'trabajador_afectado', 'descripcion', 'testigos',
            'notify_salud', 'notify_inspeccion', 'fecha_notificacion',
            'estado', 'causas',
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'}
            ),
            'centro_trabajo': forms.Select(attrs={'class': 'form-control'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'gravedad': forms.Select(attrs={'class': 'form-control'}),
            'tipo_lesion': forms.Select(attrs={'class': 'form-control'}),
            'parte_cuerpo': forms.TextInput(attrs={'class': 'form-control'}),
            'trabajador_afectado': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'testigos': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'notify_salud': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notify_inspeccion': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fecha_notificacion': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'causas': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields['centro_trabajo'].queryset = (
                self.fields['centro_trabajo'].queryset.filter(company=empresa)
            )
            self.fields['trabajador_afectado'].queryset = (
                self.fields['trabajador_afectado'].queryset.filter(company=empresa)
            )
            self.fields['causas'].queryset = CausaAccidente.objects.filter(
                models.Q(empresa=empresa) | models.Q(empresa__isnull=True),
                activa=True,
            )


class InvestigacionAccidenteForm(forms.ModelForm):
    class Meta:
        model = InvestigacionAccidente
        fields = [
            'fecha_inicio', 'metodologia', 'descripcion_ideal',
            'descripcion_real', 'causas_inmediatas', 'causas_basicas',
            'causas_organizativas', 'conclusiones', 'estado', 'investigador',
        ]
        widgets = {
            'fecha_inicio': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'metodologia': forms.Select(attrs={'class': 'form-control'}),
            'descripcion_ideal': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'descripcion_real': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'causas_inmediatas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'causas_basicas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'causas_organizativas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'conclusiones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'investigador': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            members = User.objects.filter(
                companymembership__company=empresa,
                companymembership__is_active=True,
            )
            self.fields['investigador'].queryset = members


class CausaAccidenteForm(forms.ModelForm):
    class Meta:
        model = CausaAccidente
        fields = ['nombre', 'categoria', 'activa']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class IncidenteForm(forms.ModelForm):
    class Meta:
        model = Incidente
        fields = [
            'titulo', 'fecha', 'centro_trabajo', 'ubicacion',
            'descripcion', 'potencial_dano', 'testigos',
            'trabajador_reports', 'gravedad_potencial', 'estado',
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'}
            ),
            'centro_trabajo': forms.Select(attrs={'class': 'form-control'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'potencial_dano': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'testigos': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'trabajador_reports': forms.Select(attrs={'class': 'form-control'}),
            'gravedad_potencial': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields['centro_trabajo'].queryset = (
                self.fields['centro_trabajo'].queryset.filter(company=empresa)
            )
            self.fields['trabajador_reports'].queryset = (
                self.fields['trabajador_reports'].queryset.filter(company=empresa)
            )
