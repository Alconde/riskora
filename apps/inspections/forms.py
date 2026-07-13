from django import forms
from django.contrib.auth import get_user_model

from .models import PlantillaInspeccion, PlantillaInspeccionItem, Inspeccion, ItemInspeccion

User = get_user_model()


class PlantillaInspeccionForm(forms.ModelForm):
    class Meta:
        model = PlantillaInspeccion
        fields = ['nombre', 'descripcion', 'categoria', 'activa']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PlantillaItemForm(forms.ModelForm):
    class Meta:
        model = PlantillaInspeccionItem
        fields = ['orden', 'descripcion']
        widgets = {
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'style': 'width:80px;'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


InspeccionItemFormSet = forms.inlineformset_factory(
    Inspeccion,
    ItemInspeccion,
    form=PlantillaItemForm,
    extra=1,
    can_delete=True,
)


class InspeccionForm(forms.ModelForm):
    class Meta:
        model = Inspeccion
        fields = [
            'plantilla', 'centro_trabajo', 'inspector',
            'fecha_inspeccion', 'estado', 'resultado_general',
            'observaciones', 'fotos',
        ]
        widgets = {
            'plantilla': forms.Select(attrs={'class': 'form-control'}),
            'centro_trabajo': forms.Select(attrs={'class': 'form-control'}),
            'inspector': forms.Select(attrs={'class': 'form-control'}),
            'fecha_inspeccion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'resultado_general': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields['plantilla'].queryset = PlantillaInspeccion.objects.filter(
                empresa=empresa, activa=True
            )
            self.fields['centro_trabajo'].queryset = (
                self.fields['centro_trabajo'].queryset.filter(company=empresa)
            )
            members = User.objects.filter(
                companymembership__company=empresa,
                companymembership__is_active=True,
            )
            self.fields['inspector'].queryset = members


class ItemInspeccionForm(forms.ModelForm):
    class Meta:
        model = ItemInspeccion
        fields = ['orden', 'descripcion', 'resultado', 'observaciones', 'foto']
        widgets = {
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'style': 'width:80px;'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'resultado': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
