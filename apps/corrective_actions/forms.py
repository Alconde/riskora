from django import forms
from django.contrib.auth import get_user_model

from .models import NoConformidad, AccionCorrectiva, AccionPreventiva

User = get_user_model()


class NoConformidadForm(forms.ModelForm):
    class Meta:
        model = NoConformidad
        fields = [
            'titulo', 'descripcion', 'fuente', 'gravedad', 'estado',
            'centro_trabajo', 'trabajador', 'ubicacion',
            'fecha_deteccion', 'fecha_limite_resolucion',
            'causa_raiz', 'metodo_causa_raiz',
            'evidencias', 'archivo_evidencia',
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'fuente': forms.Select(attrs={'class': 'form-control'}),
            'gravedad': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'centro_trabajo': forms.Select(attrs={'class': 'form-control'}),
            'trabajador': forms.Select(attrs={'class': 'form-control'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_deteccion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_limite_resolucion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'causa_raiz': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'metodo_causa_raiz': forms.Select(attrs={'class': 'form-control'}),
            'evidencias': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields['centro_trabajo'].queryset = (
                self.fields['centro_trabajo'].queryset.filter(company=empresa)
            )
            self.fields['trabajador'].queryset = (
                self.fields['trabajador'].queryset.filter(company=empresa)
            )


class NoConformidadCerrarForm(forms.Form):
    resuelta_en = forms.DateField(
        label='Fecha de resolucion',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    notas_verificacion = forms.CharField(
        label='Notas de verificacion',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    )


class AccionCorrectivaForm(forms.ModelForm):
    class Meta:
        model = AccionCorrectiva
        fields = [
            'descripcion', 'responsable', 'fecha_limite', 'estado',
            'fecha_ejecucion', 'evidencia_implementacion', 'archivo_evidencia',
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'responsable': forms.Select(attrs={'class': 'form-control'}),
            'fecha_limite': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'fecha_ejecucion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'evidencia_implementacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            members = User.objects.filter(
                companymembership__company=empresa,
                companymembership__is_active=True,
            )
            self.fields['responsable'].queryset = members


class AccionPreventivaForm(forms.ModelForm):
    class Meta:
        model = AccionPreventiva
        fields = [
            'titulo', 'descripcion', 'responsable', 'fecha_limite', 'estado',
            'fecha_ejecucion', 'no_conformidad_origen',
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'responsable': forms.Select(attrs={'class': 'form-control'}),
            'fecha_limite': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'fecha_ejecucion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'no_conformidad_origen': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            members = User.objects.filter(
                companymembership__company=empresa,
                companymembership__is_active=True,
            )
            self.fields['responsable'].queryset = members
            self.fields['no_conformidad_origen'].queryset = (
                NoConformidad.objects.filter(empresa=empresa)
            )
