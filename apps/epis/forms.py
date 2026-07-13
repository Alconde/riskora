from django import forms
from django.contrib.auth import get_user_model

from .models import CatalogoEPI, EPI, EntregaEPI, InspeccionEPI, ProcedimientoEntrega, FirmaEntrega

User = get_user_model()


class EPIForm(forms.ModelForm):
    class Meta:
        model = EPI
        fields = [
            'catalogo', 'marca', 'modelo', 'numero_serie',
            'vida_util_meses', 'precio', 'proveedor',
            'fecha_compra', 'estado', 'activo',
        ]
        widgets = {
            'catalogo': forms.Select(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_serie': forms.TextInput(attrs={'class': 'form-control'}),
            'vida_util_meses': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'proveedor': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_compra': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['catalogo'].queryset = CatalogoEPI.objects.filter(activo=True)


class EntregaEPIForm(forms.ModelForm):
    class Meta:
        model = EntregaEPI
        fields = [
            'epi', 'trabajador', 'fecha_entrega', 'fecha_caducidad',
            'estado', 'motivo_devolucion', 'firma_trabajador',
        ]
        widgets = {
            'epi': forms.Select(attrs={'class': 'form-control'}),
            'trabajador': forms.Select(attrs={'class': 'form-control'}),
            'fecha_entrega': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_caducidad': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'motivo_devolucion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'firma_trabajador': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields['epi'].queryset = EPI.objects.filter(empresa=empresa, activo=True)
            self.fields['trabajador'].queryset = (
                self.fields['trabajador'].queryset.filter(company=empresa)
            )


class InspeccionEPIForm(forms.ModelForm):
    class Meta:
        model = InspeccionEPI
        fields = [
            'epi', 'entrega', 'fecha', 'resultado',
            'observaciones', 'inspeccionado_por',
        ]
        widgets = {
            'epi': forms.Select(attrs={'class': 'form-control'}),
            'entrega': forms.Select(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'resultado': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'inspeccionado_por': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields['epi'].queryset = EPI.objects.filter(empresa=empresa, activo=True)
            self.fields['entrega'].queryset = EntregaEPI.objects.filter(
                empresa=empresa, estado='activo'
            )
            members = User.objects.filter(
                companymembership__company=empresa,
                companymembership__is_active=True,
            )
            self.fields['inspeccionado_por'].queryset = members


class ProcedimientoEntregaForm(forms.ModelForm):
    class Meta:
        model = ProcedimientoEntrega
        fields = ['titulo', 'descripcion', 'archivo', 'version', 'activo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'version': forms.TextInput(attrs={'class': 'form-control', 'style': 'width:100px;'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class FirmaEntregaForm(forms.ModelForm):
    class Meta:
        model = FirmaEntrega
        fields = ['entrega', 'trabajador', 'estado_firma', 'archivo_firmado', 'fecha_firma', 'notas']
        widgets = {
            'entrega': forms.Select(attrs={'class': 'form-control'}),
            'trabajador': forms.Select(attrs={'class': 'form-control'}),
            'estado_firma': forms.Select(attrs={'class': 'form-control'}),
            'fecha_firma': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields['entrega'].queryset = EntregaEPI.objects.filter(empresa=empresa)
            self.fields['trabajador'].queryset = (
                self.fields['trabajador'].queryset.filter(company=empresa)
            )


class FirmaEntregaUploadForm(forms.ModelForm):
    class Meta:
        model = FirmaEntrega
        fields = ['archivo_firmado', 'fecha_firma']
        widgets = {
            'fecha_firma': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
