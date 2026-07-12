from django import forms

from .models import Task, Alert


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'company',
            'title',
            'description',
            'status',
            'priority',
            'assigned_to',
            'due_date',
            'notes',
        ]
        widgets = {
            'company': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['due_date'].input_formats = ['%Y-%m-%d']
        if empresa:
            from apps.accounts.models import User
            user_ids = empresa.memberships.filter(
                is_active=True
            ).values_list('user_id', flat=True)
            self.fields['assigned_to'].queryset = User.objects.filter(
                id__in=user_ids
            )
