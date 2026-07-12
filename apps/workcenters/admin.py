from django.contrib import admin
from .models import WorkCenter


@admin.register(WorkCenter)
class WorkCenterAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'city', 'province', 'risk_level', 'is_active')
    search_fields = ('name', 'company__legal_name', 'city', 'province')
    list_filter = ('risk_level', 'is_active', 'province')
