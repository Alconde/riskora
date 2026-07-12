from django.contrib import admin
from .models import Alert, Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'company',
        'status',
        'priority',
        'assigned_to',
        'due_date',
        'created_at',
    )
    search_fields = (
        'title',
        'description',
        'company__legal_name',
        'assigned_to__username',
        'assigned_to__email',
    )
    list_filter = (
        'status',
        'priority',
        'company',
        'due_date',
    )
    readonly_fields = ('completed_at', 'created_at', 'updated_at')


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'company',
        'alert_type',
        'severity',
        'is_active',
        'is_read',
        'due_date',
        'created_at',
    )
    search_fields = (
        'title',
        'message',
        'company__legal_name',
    )
    list_filter = (
        'alert_type',
        'severity',
        'is_active',
        'is_read',
        'company',
    )
    readonly_fields = ('read_at', 'created_at', 'updated_at')
