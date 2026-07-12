from django import forms

from .models import Document


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = [
            'company',
            'category',
            'title',
            'description',
            'file',
            'version',
            'code',
            'issue_date',
            'review_date',
            'expiry_date',
            'status',
            'is_confidential',
            'notes',
        ]
        widgets = {
            'company': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'version': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'review_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'is_confidential': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()

        issue_date = cleaned_data.get('issue_date')
        review_date = cleaned_data.get('review_date')
        expiry_date = cleaned_data.get('expiry_date')
        status = cleaned_data.get('status')

        if issue_date and review_date and review_date < issue_date:
            self.add_error('review_date', 'La fecha de revisión no puede ser anterior a la fecha de emisión.')

        if issue_date and expiry_date and expiry_date < issue_date:
            self.add_error('expiry_date', 'La fecha de caducidad no puede ser anterior a la fecha de emisión.')

        if status == Document.Status.EXPIRED and not expiry_date:
            self.add_error('expiry_date', 'Si el documento está caducado, debes indicar una fecha de caducidad.')

        return cleaned_data