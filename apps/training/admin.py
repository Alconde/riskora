from django.contrib import admin

from .models import (
    TrainingCategory,
    TrainingCourse,
    TrainingDocument,
    TrainingRecord,
)


@admin.register(TrainingCategory)
class TrainingCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'code', 'description')
    ordering = ('name',)


@admin.register(TrainingCourse)
class TrainingCourseAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'company',
        'category',
        'modality',
        'duration_hours',
        'is_mandatory',
        'requires_renewal',
        'status',
        'created_at',
    )
    list_filter = (
        'status',
        'modality',
        'is_mandatory',
        'requires_renewal',
        'category',
        'company',
    )
    search_fields = (
        'name',
        'code',
        'description',
        'objective',
        'content',
        'company__legal_name',
        'company__trade_name',
        'category__name',
    )
    autocomplete_fields = ('company',)
    filter_horizontal = ('required_for_job_positions',)
    ordering = ('name',)


class TrainingDocumentInline(admin.TabularInline):
    model = TrainingDocument
    extra = 0
    fields = ('name', 'document_type', 'file', 'notes', 'uploaded_at')
    readonly_fields = ('uploaded_at',)


@admin.register(TrainingRecord)
class TrainingRecordAdmin(admin.ModelAdmin):
    list_display = (
        'worker',
        'company',
        'job_position',
        'course',
        'status',
        'planned_date',
        'completed_date',
        'expiry_date',
        'created_at',
    )
    list_filter = (
        'status',
        'company',
        'job_position',
        'course__category',
        'course',
        'completed_date',
        'expiry_date',
    )
    search_fields = (
        'worker__first_name',
        'worker__last_name',
        'worker__national_id',
        'worker__employee_code',
        'course__name',
        'course__code',
        'certificate_number',
        'trainer_name',
        'training_entity',
        'company__legal_name',
        'company__trade_name',
    )
    autocomplete_fields = ('company', 'worker', 'job_position', 'course')
    inlines = [TrainingDocumentInline]
    ordering = ('-completed_date', '-planned_date', '-created_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TrainingDocument)
class TrainingDocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'record', 'document_type', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = (
        'name',
        'document_type',
        'notes',
        'record__worker__first_name',
        'record__worker__last_name',
        'record__course__name',
    )
    autocomplete_fields = ('record',)
    ordering = ('-uploaded_at',)
    readonly_fields = ('uploaded_at',)