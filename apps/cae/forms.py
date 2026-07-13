from django import forms
from .models import (
    EmpresaSubcontrata, DocumentoCAE, ProcedimientoCAE,
    CartaCAE, DocumentoRiesgosCAE,
)


class EmpresaSubcontrataForm(forms.ModelForm):
    class Meta:
        model = EmpresaSubcontrata
        fields = [
            'nombre_empresa', 'trabajo_realizar', 'persona_contacto',
            'telefono', 'email', 'activa',
        ]
        widgets = {
            'trabajo_realizar': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class DocumentoCAEForm(forms.ModelForm):
    class Meta:
        model = DocumentoCAE
        fields = ['documento', 'fecha_caducidad']
        widgets = {
            'documento': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf,.png,.jpg,.jpeg'}),
            'fecha_caducidad': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class ProcedimientoCAEForm(forms.ModelForm):
    class Meta:
        model = ProcedimientoCAE
        fields = ['documento', 'version', 'fecha']
        widgets = {
            'documento': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class CartaCAEForm(forms.ModelForm):
    class Meta:
        model = CartaCAE
        fields = ['documento']
        widgets = {
            'documento': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        }


class DocumentoRiesgosCAEForm(forms.ModelForm):
    class Meta:
        model = DocumentoRiesgosCAE
        fields = ['documento']
        widgets = {
            'documento': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        }
