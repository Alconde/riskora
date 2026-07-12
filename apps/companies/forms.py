from django import forms

from apps.companies.models import Company, CompanyMembership

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'legal_name',
            'trade_name',
            'tax_id',
            'email',
            'phone',
            'website',
            'address',
            'postal_code',
            'city',
            'province',
            'autonomous_community',
            'country',
            'activity',
            'cnae',
            'workforce_size',
            'status',
            'notes',
        ]
        widgets = {
            'legal_name': forms.TextInput(attrs={'class': 'form-control'}),
            'trade_name': forms.TextInput(attrs={'class': 'form-control'}),
            'tax_id': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'province': forms.TextInput(attrs={'class': 'form-control'}),
            'autonomous_community': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'activity': forms.TextInput(attrs={'class': 'form-control'}),
            'cnae': forms.TextInput(attrs={'class': 'form-control'}),
            'workforce_size': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class ActiveCompanyForm(forms.Form):
    company = forms.ModelChoiceField(
        queryset=Company.objects.none(),
        empty_label=None,
        label='Empresa'
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        memberships = CompanyMembership.objects.select_related('company').filter(
            user=user,
            is_active=True,
            company__status='active'
        ).order_by('company__legal_name')

        company_ids = memberships.values_list('company_id', flat=True)
        self.fields['company'].queryset = Company.objects.filter(id__in=company_ids).order_by('legal_name')