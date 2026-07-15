from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User
from apps.companies.models import CompanyMembership


class CompanyMembershipInline(admin.TabularInline):
    model = CompanyMembership
    fk_name = 'user'
    extra = 0
    autocomplete_fields = ('company',)
    fields = ('company', 'role', 'is_active', 'is_default', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('company',)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': ('role', 'phone', 'job_title', 'is_verified'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información adicional', {
            'fields': ('email', 'role', 'phone', 'job_title', 'is_verified'),
        }),
    )

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'is_verified',
        'is_staff',
        'is_active',
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('role', 'is_verified', 'is_staff', 'is_superuser', 'is_active')
    ordering = ('username',)
    inlines = (CompanyMembershipInline,)