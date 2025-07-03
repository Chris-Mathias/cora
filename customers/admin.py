from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'type',
        'email',
        'phone_primary',
        'is_active',
        'created_at',
        'updated_at',
    )
    search_fields = ('name', 'email', 'phone_primary')
    list_filter = ('type', 'is_active', 'created_at')
    ordering = ('-created_at',)
    list_per_page = 20
    date_hierarchy = 'created_at'
