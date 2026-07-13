from django import forms
from .models import ProductoQuimico, ClasificacionQuimica


class ProductoQuimicoForm(forms.ModelForm):
    class Meta:
        model = ProductoQuimico
        fields = ['nombre', 'fabricante', 'composicion', 'uso', 'ubicacion',
                  'ficha_seguridad', 'imagen_etiqueta', 'fecha_caducidad',
                  'stock', 'unidad', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'fabricante': forms.TextInput(attrs={'class': 'form-control'}),
            'composicion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'uso': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_caducidad': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unidad': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ClasificacionQuimicaForm(forms.ModelForm):
    class Meta:
        model = ClasificacionQuimica
        fields = ['pictograma', 'frase_riesgo', 'frase_precaucion']
        widgets = {
            'frase_riesgo': forms.TextInput(attrs={'class': 'form-control'}),
            'frase_precaucion': forms.TextInput(attrs={'class': 'form-control'}),
        }
