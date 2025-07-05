from django.contrib import admin

from .models import PurchaseOrder, PurchaseOrderItem, PurchaseOrderStatus


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    autocomplete_fields = ['product']
    fields = ('product', 'quantity', 'unit_price')


@admin.register(PurchaseOrderStatus)
class PurchaseOrderStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'sequence_order', 'tenant')
    list_filter = ('tenant',)
    search_fields = ('name',)


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'status', 'total_amount', 'created_at', 'tenant')
    list_filter = ('status', 'tenant', 'created_at')
    search_fields = ('id', 'supplier__name')
    autocomplete_fields = ['supplier', 'status', 'tenant']
    inlines = [PurchaseOrderItemInline]

    fieldsets = (
        ('Informações Principais', {
            'fields': ('tenant', 'supplier', 'status')
        }),
        ('Datas e Valores', {
            'fields': ('expected_delivery_date', 'total_amount')
        }),
        ('Observações', {
            'fields': ('notes',)
        }),
        ('Datas de Controlo', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    readonly_fields = ('total_amount', 'created_at', 'updated_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('supplier', 'status', 'tenant')


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'purchase_order', 'product', 'quantity', 'unit_price')
    list_filter = ('purchase_order__tenant',)
    search_fields = ('purchase_order__id', 'product__name')
    autocomplete_fields = ['purchase_order', 'product']
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('purchase_order', 'product')
