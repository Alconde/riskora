from django import forms
from django.contrib.auth import get_user_model

from .models import EnfermedadProfesional, InvestigacionEEPP, ProcedimientoInvestigacionEEPP

User = get_user_model()


class EnfermedadProfesionalForm(forms.ModelForm):
    class Meta:
        model = EnfermedadProfesional
        fields = [
            'titulo', 'fecha_diagnostico', 'centro_trabajo',
            'trabajador_afectado', 'nombre_enfermedad', 'agente_causante',
            'tipo_exposicion', 'duracion_exposicion', 'parte_cuerpo',
            'gravedad', 'descripcion', 'testigos',
            'notify_salud', 'notify_inspeccion', 'estado',
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_diagnostico': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'centro_trabajo': forms.Select(attrs={'class': 'form-control'}),
            'trabajador_afectado': forms.Select(attrs={'class': 'form-control'}),
            'nombre_enfermedad': forms.TextInput(attrs={'class': 'form-control'}),
            'agente_causante': forms.Select(attrs={'class': 'form-control'}),
            'tipo_exposicion': forms.TextInput(attrs={'class': 'form-control'}),
            'duracion_exposicion': forms.TextInput(attrs={'class': 'form-control'}),
            'parte_cuerpo': forms.TextInput(attrs={'class': 'form-control'}),
            'gravedad': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'testigos': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'notify_salud': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notify_inspeccion': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            from apps.workers.models import Worker
            from apps.workcenters.models import WorkCenter
            self.fields['trabajador_afectado'].queryset = Worker.objects.filter(
                companymembership__company=empresa,
                companymembership__is_active=True,
            )
            self.fields['centro_trabajo'].queryset = WorkCenter.objects.filter(
                empresa=empresa
            )


class InvestigacionEEPPForm(forms.ModelForm):
    class Meta:
        model = InvestigacionEEPP
        fields = [
            'fecha_inicio', 'metodologia', 'puesto_trabajo',
            'horas_trabajador', 'hora_dia', 'edad', 'tiempo_puesto',
            'acto_condicion_detectada', 'riesgo_identificado',
            'medidas_preventivas', 'plazo', 'responsable', 'coste',
            'riesgo_en_er',
            'descripcion_ideal', 'descripcion_real',
            'causas_inmediatas', 'causas_basicas', 'causas_organizativas',
            'conclusiones', 'estado', 'investigador', 'revisor', 'fecha_firma',
        ]
        widgets = {
            'fecha_inicio': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'metodologia': forms.Select(attrs={'class': 'form-control'}),
            'puesto_trabajo': forms.TextInput(attrs={'class': 'form-control'}),
            'horas_trabajador': forms.NumberInput(
                attrs={'class': 'form-control', 'min': 1, 'max': 8}
            ),
            'hora_dia': forms.TimeInput(
                attrs={'class': 'form-control', 'type': 'time'}
            ),
            'edad': forms.NumberInput(attrs={'class': 'form-control'}),
            'tiempo_puesto': forms.TextInput(attrs={'class': 'form-control'}),
            'acto_condicion_detectada': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
            'riesgo_identificado': forms.Select(attrs={'class': 'form-control'}),
            'medidas_preventivas': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
            'plazo': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'responsable': forms.Select(attrs={'class': 'form-control'}),
            'coste': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01'}
            ),
            'riesgo_en_er': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
            'descripcion_ideal': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
            'descripcion_real': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
            'causas_inmediatas': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
            'causas_basicas': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
            'causas_organizativas': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
            'conclusiones': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'investigador': forms.Select(attrs={'class': 'form-control'}),
            'revisor': forms.Select(attrs={'class': 'form-control'}),
            'fecha_firma': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            members = User.objects.filter(
                companymembership__company=empresa,
                companymembership__is_active=True,
            )
            self.fields['investigador'].queryset = members
            self.fields['responsable'].queryset = members
            self.fields['revisor'].queryset = members


class ProcedimientoInvestigacionEEPPForm(forms.ModelForm):
    class Meta:
        model = ProcedimientoInvestigacionEEPP
        fields = ['titulo', 'descripcion', 'archivo', 'version', 'activo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'version': forms.TextInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
