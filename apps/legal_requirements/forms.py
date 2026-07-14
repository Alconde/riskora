from django import forms
from .models import NormativaLegal, RequisitoLegal, CumplimientoLegal, AlertaLegal


class NormativaLegalForm(forms.ModelForm):
    class Meta:
        model = NormativaLegal
        fields = [
            'nombre', 'tipo', 'numero', 'ambito', 'comunidad_autonoma',
            'fecha_publicacion', 'fecha_vigencia', 'fecha_fin_vigencia',
            'boe_enlace', 'resumen', 'activa', 'notas_internas',
        ]
        widgets = {
            'nombre': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'ambito': forms.Select(attrs={'class': 'form-control'}),
            'comunidad_autonoma': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_publicacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_vigencia': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin_vigencia': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'boe_enlace': forms.URLInput(attrs={'class': 'form-control'}),
            'resumen': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notas_internas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class RequisitoLegalForm(forms.ModelForm):
    class Meta:
        model = RequisitoLegal
        fields = [
            'normativa', 'titulo', 'descripcion', 'categoria',
            'articulo', 'plazo_cumplimiento', 'observaciones',
        ]
        widgets = {
            'normativa': forms.Select(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'articulo': forms.TextInput(attrs={'class': 'form-control'}),
            'plazo_cumplimiento': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class CumplimientoLegalForm(forms.ModelForm):
    class Meta:
        model = CumplimientoLegal
        fields = [
            'requisito', 'estado', 'fecha_evaluacion', 'fecha_proxima_revision',
            'evidencia', 'acciones_necesarias', 'responsable', 'notas',
        ]
        widgets = {
            'requisito': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'fecha_evaluacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_proxima_revision': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'evidencia': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'acciones_necesarias': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'responsable': forms.Select(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            from apps.companies.models import CompanyMembership
            usuarios = CompanyMembership.objects.filter(
                empresa=empresa,
            ).values_list('usuario_id', flat=True)
            from django.contrib.auth import get_user_model
            User = get_user_model()
            self.fields['responsable'].queryset = User.objects.filter(id__in=usuarios)
            self.fields['requisito'].queryset = RequisitoLegal.objects.filter(
                normativa__activa=True,
            )


class CumplimientoBulkForm(forms.Form):
    """Form para crear cumplimientos masivos desde la normativa."""
    normativas = forms.MultipleChoiceField(
        label='Seleccionar normativas para evaluar',
        choices=[],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True,
    )

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        existentes = CumplimientoLegal.objects.filter(
            empresa=empresa,
        ).values_list('requisito_id', flat=True)
        from .models import NormativaLegal
        normativas = NormativaLegal.objects.filter(activa=True)
        choices = []
        for norm in normativas:
            for req in norm.requisitos.all():
                if req.id not in existentes:
                    choices.append((req.id, f'{norm} — {req.titulo[:80]}'))
        self.fields['normativas'].choices = choices


class AlertaLegalForm(forms.ModelForm):
    class Meta:
        model = AlertaLegal
        fields = ['leida', 'resuelta']
        widgets = {
            'leida': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'resuelta': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
