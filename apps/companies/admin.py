from django.contrib import admin

from .models import Company, CompanyMembership


class CompanyMembershipInline(admin.TabularInline):
    model = CompanyMembership
    extra = 0
    autocomplete_fields = ('user',)
    fields = ('user', 'role', 'is_active', 'is_default', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('user',)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        'legal_name',
        'trade_name',
        'tax_id',
        'city',
        'province',
        'status',
        'workforce_size',
        'created_at',
    )
    search_fields = (
        'legal_name',
        'trade_name',
        'tax_id',
        'city',
        'province',
        'email',
        'activity',
        'cnae',
    )
    list_filter = ('status', 'province', 'autonomous_community', 'country')
    ordering = ('legal_name',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = (CompanyMembershipInline,)

    fieldsets = (
        ('Identificación', {
            'fields': ('legal_name', 'trade_name', 'tax_id', 'status', 'logo'),
        }),
        ('Contacto', {
            'fields': ('email', 'phone', 'website'),
        }),
        ('Ubicación', {
            'fields': (
                'address',
                'postal_code',
                'city',
                'province',
                'autonomous_community',
                'country',
            ),
        }),
        ('Actividad', {
            'fields': ('activity', 'cnae', 'workforce_size'),
        }),
        ('Observaciones', {
            'fields': ('notes',),
        }),
        ('Trazabilidad', {
            'fields': ('created_at', 'updated_at'),
        }),
    )


@admin.register(CompanyMembership)
class CompanyMembershipAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'company',
        'role',
        'is_active',
        'is_default',
        'created_at',
    )
    search_fields = (
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
        'company__legal_name',
        'company__trade_name',
        'company__tax_id',
    )
    list_filter = ('role', 'is_active', 'is_default', 'company__status')
    autocomplete_fields = ('user', 'company')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('company__legal_name', 'user__username')
    list_select_related = ('user', 'company')

    fieldsets = (
        ('Relación', {
            'fields': ('user', 'company', 'role'),
        }),
        ('Estado', {
            'fields': ('is_active', 'is_default'),
        }),
        ('Trazabilidad', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'company')