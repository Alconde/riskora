from django.contrib import admin
from .models import Document, DocumentCategory


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'scope', 'is_mandatory', 'default_validity_days', 'is_active')
    search_fields = ('name', 'slug')
    list_filter = ('scope', 'is_mandatory', 'is_active')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'company',
        'category',
        'status',
        'issue_date',
        'expiry_date',
        'uploaded_by',
        'created_at',
    )
    search_fields = (
        'title',
        'code',
        'company__legal_name',
        'category__name',
    )
    list_filter = (
        'status',
        'category',
        'is_confidential',
        'company',
    )
    readonly_fields = ('id', 'created_at', 'updated_at')
