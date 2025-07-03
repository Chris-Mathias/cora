from django.contrib import admin

from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'tenant',
        'type',
        'email',
        'phone_primary',
        'is_active',
        'created_at',
        'updated_at',
    )
    search_fields = ('name', 'email', 'phone_primary')
    list_filter = ('tenant', 'type', 'is_active')
    ordering = ('-created_at',)
    list_per_page = 20
    date_hierarchy = 'created_at'
