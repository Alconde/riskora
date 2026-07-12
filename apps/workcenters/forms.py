from django import forms

from apps.workcenters.models import WorkCenter


class WorkCenterForm(forms.ModelForm):
    class Meta:
        model = WorkCenter
        fields = [
            'company',
            'name',
            'code',
            'address',
            'postal_code',
            'city',
            'province',
            'contact_person',
            'contact_phone',
            'contact_email',
            'activity',
            'worker_count',
            'risk_level',
            'is_active',
            'notes',
        ]
        widgets = {
            'company': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'province': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'activity': forms.TextInput(attrs={'class': 'form-control'}),
            'worker_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'risk_level': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }