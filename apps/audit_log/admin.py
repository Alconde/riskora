from django.contrib import admin
from apps.audit_log.models import AuditLog, RetentionPolicy


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        'timestamp', 'user', 'action', 'model_name',
        'object_id', 'origin', 'empresa',
    )
    list_filter = ('action', 'origin', 'model_name')
    search_fields = ('object_repr', 'user__username', 'user__email')
    readonly_fields = (
        'request_id', 'trace_id', 'parent_event_id',
        'user', 'empresa', 'origin', 'ip_address', 'user_agent',
        'action', 'model_name', 'object_id', 'object_repr',
        'changes', 'timestamp',
    )
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(RetentionPolicy)
class RetentionPolicyAdmin(admin.ModelAdmin):
    list_display = ('category', 'retention_days', 'anonymize', 'is_active')
    list_filter = ('is_active', 'anonymize')
