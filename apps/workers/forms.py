from django import forms

from apps.workers.models import Worker, JobPosition
from apps.workcenters.models import WorkCenter


class WorkerForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = [
            'company',
            'work_center',
            'job_position',
            'user',
            'first_name',
            'last_name',
            'national_id',
            'email',
            'phone',
            'employee_code',
            'social_security_number',
            'hire_date',
            'birth_date',
            'employment_status',
            'especially_sensitive',
            'temporary_worker',
            'notes',
        ]
        widgets = {
            'company': forms.Select(attrs={'class': 'form-control'}),
            'work_center': forms.Select(attrs={'class': 'form-control'}),
            'job_position': forms.Select(attrs={'class': 'form-control'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'national_id': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'employee_code': forms.TextInput(attrs={'class': 'form-control'}),
            'social_security_number': forms.TextInput(attrs={'class': 'form-control'}),
            'hire_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'employment_status': forms.Select(attrs={'class': 'form-control'}),
            'especially_sensitive': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'temporary_worker': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['hire_date'].input_formats = ['%Y-%m-%d']
        self.fields['birth_date'].input_formats = ['%Y-%m-%d']
        self.fields['national_id'].required = False
        self.fields['social_security_number'].required = False
        self.fields['employee_code'].required = False
        self.fields['user'].required = False

        self.fields['work_center'].queryset = WorkCenter.objects.none()
        self.fields['job_position'].queryset = JobPosition.objects.none()

        if 'company' in self.data:
            try:
                company_id = int(self.data.get('company'))
                self.fields['work_center'].queryset = WorkCenter.objects.filter(
                    company_id=company_id
                ).order_by('name')
                self.fields['job_position'].queryset = JobPosition.objects.filter(
                    company_id=company_id
                ).order_by('name')
            except (ValueError, TypeError):
                pass

        elif self.instance.pk and self.instance.company_id:
            self.fields['work_center'].queryset = WorkCenter.objects.filter(
                company=self.instance.company
            ).order_by('name')
            self.fields['job_position'].queryset = JobPosition.objects.filter(
                company=self.instance.company
            ).order_by('name')

    def clean_employee_code(self):
        value = self.cleaned_data.get('employee_code')
        return value or None

    def clean_national_id(self):
        value = self.cleaned_data.get('national_id')
        return value or None

    def clean_social_security_number(self):
        value = self.cleaned_data.get('social_security_number')
        return value or None