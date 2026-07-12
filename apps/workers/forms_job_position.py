from django import forms

from apps.workers.models import JobPosition


class JobPositionForm(forms.ModelForm):
    class Meta:
        model = JobPosition
        fields = [
            'company',
            'name',
            'department',
            'description',
            'status',
            'notes',
        ]
        widgets = {
            'company': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }