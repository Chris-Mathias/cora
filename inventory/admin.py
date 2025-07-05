from django.contrib import admin

from .models import (StockAdjustment, StockAdjustmentItem, StockAdjustmentType,
                     StockEntry, StockEntryItem, StockMovement)


class StockEntryItemInline(admin.TabularInline):
    model = StockEntryItem
    extra = 1
    autocomplete_fields = ['product']
    fields = ('product', 'quantity', 'unit_price', 'expiration_date')


class StockAdjustmentItemInline(admin.TabularInline):
    model = StockAdjustmentItem
    extra = 1
    autocomplete_fields = ['product', 'adjustment_type']
    fields = ('product', 'adjustment_type', 'quantity', 'notes')


@admin.register(StockEntry)
class StockEntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'purchase', 'status', 'created_at', 'tenant')
    list_filter = ('status', 'tenant', 'created_at')
    search_fields = ('id', 'supplier__name', 'purchase__id', 'notes')
    autocomplete_fields = ['tenant', 'purchase', 'supplier', 'user']
    inlines = [StockEntryItemInline]
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Informações Principais', {
            'fields': ('tenant', 'status', 'supplier', 'purchase', 'user')
        }),
        ('Observações', {
            'fields': ('notes',)
        }),
        ('Datas de Controle', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(StockEntryItem)
class StockEntryItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'stock_entry', 'product', 'quantity', 'unit_price', 'expiration_date')
    list_filter = ('stock_entry__tenant', 'product')
    search_fields = ('product__name', 'stock_entry__id')
    autocomplete_fields = ['product', 'stock_entry']
    readonly_fields = ('created_at', 'updated_at')


@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'user', 'created_at', 'tenant')
    list_filter = ('status', 'tenant')
    search_fields = ('id', 'notes')
    autocomplete_fields = ['tenant', 'user']
    inlines = [StockAdjustmentItemInline]
    readonly_fields = ('created_at', 'updated_at')


@admin.register(StockAdjustmentItem)
class StockAdjustmentItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'adjustment_type', 'quantity', 'notes')
    list_filter = ('adjustment_type', 'tenant')
    search_fields = ('product__name', 'notes')
    autocomplete_fields = ['product', 'adjustment_type']
    readonly_fields = ('created_at', 'updated_at')


@admin.register(StockAdjustmentType)
class StockAdjustmentTypeAdmin(admin.ModelAdmin):
    list_display = ('label', 'name', 'direction', 'tenant')
    list_filter = ('direction', 'tenant')
    search_fields = ('name', 'label')


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'product', 'direction', 'quantity', 'new_stock', 'source_document')
    list_filter = ('direction', 'tenant', 'created_at')
    search_fields = ('product__name', 'notes')
    readonly_fields = [f.name for f in StockMovement._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'tenant', 'user', 'source_content_type')
