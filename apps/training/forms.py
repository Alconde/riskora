from django import forms

from .models import TrainingCategory, TrainingCourse, TrainingRecord


class BaseStyledModelForm(forms.ModelForm):
    """
    Clase base simple para aplicar clases CSS comunes a los campos.
    Útil si luego usas Bootstrap.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            widget = field.widget

            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault('class', 'form-check-input')
            elif isinstance(widget, (forms.Select, forms.SelectMultiple, forms.DateInput, forms.DateTimeInput)):
                widget.attrs.setdefault('class', 'form-select')
            elif isinstance(widget, forms.Textarea):
                widget.attrs.setdefault('class', 'form-control')
                widget.attrs.setdefault('rows', 3)
            else:
                widget.attrs.setdefault('class', 'form-control')


class TrainingCategoryForm(BaseStyledModelForm):
    class Meta:
        model = TrainingCategory
        fields = [
            'name',
            'code',
            'description',
            'is_active',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class TrainingCourseForm(BaseStyledModelForm):
    class Meta:
        model = TrainingCourse
        fields = [
            'company',
            'category',
            'required_for_job_positions',
            'name',
            'code',
            'description',
            'objective',
            'content',
            'modality',
            'duration_hours',
            'is_mandatory',
            'requires_renewal',
            'validity_value',
            'validity_unit',
            'status',
            'notes',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'objective': forms.Textarea(attrs={'rows': 3}),
            'content': forms.Textarea(attrs={'rows': 4}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['required_for_job_positions'].widget.attrs['class'] = 'form-select'
        self.fields['required_for_job_positions'].widget.attrs['size'] = 8


class TrainingRecordForm(BaseStyledModelForm):
    class Meta:
        model = TrainingRecord
        fields = [
            'company',
            'worker',
            'job_position',
            'course',
            'status',
            'planned_date',
            'completed_date',
            'expiry_date',
            'trainer_name',
            'training_entity',
            'certificate_number',
            'attendance_percentage',
            'score',
            'notes',
        ]
        widgets = {
            'planned_date': forms.DateInput(attrs={'type': 'date'}),
            'completed_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }