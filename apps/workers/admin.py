from django.contrib import admin

from apps.workers.models import Worker, JobPosition


@admin.register(JobPosition)
class JobPositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'department', 'status', 'created_at')
    search_fields = ('name', 'department', 'company__trade_name', 'company__legal_name')
    list_filter = ('status', 'company')


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'company', 'work_center', 'job_position', 'employment_status')
    search_fields = ('first_name', 'last_name', 'national_id', 'employee_code', 'company__trade_name')
    list_filter = ('company', 'work_center', 'employment_status', 'especially_sensitive', 'temporary_worker')