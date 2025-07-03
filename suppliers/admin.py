from django.contrib import admin

from .models import Supplier, SupplierProduct


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


@admin.register(SupplierProduct)
class SupplierProductAdmin(admin.ModelAdmin):
    list_display = (
        'supplier',
        'tenant',
        'product',
        'cost_price',
        'supplier_code',
        'created_at',
        'updated_at',
    )
    search_fields = ('supplier__name', 'product__name')
    list_filter = ('tenant',)
    ordering = ('-created_at',)
    list_per_page = 20
    date_hierarchy = 'created_at'
