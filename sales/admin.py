from django.contrib import admin

from .models import SaleOrder, SaleOrderHistory, SaleOrderItem, SaleOrderStatus


class SaleOrderItemInline(admin.TabularInline):
    model = SaleOrderItem
    extra = 1
    autocomplete_fields = ['product']
    readonly_fields = ('total_amount',)
    fields = ('product', 'quantity', 'unit_price', 'discount_amount', 'taxes_amount', 'total_amount')


class SaleOrderHistoryInline(admin.TabularInline):
    model = SaleOrderHistory
    extra = 0
    readonly_fields = ('status', 'notes', 'created_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(SaleOrderStatus)
class SaleOrderStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'label', 'sequence_order', 'tenant', 'color_code')
    list_filter = ('tenant',)
    search_fields = ('name',)


@admin.register(SaleOrder)
class SaleOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'total_amount', 'created_at', 'tenant')
    list_filter = ('status', 'tenant', 'created_at')
    search_fields = ('id', 'customer__name')
    autocomplete_fields = ['customer', 'salesperson', 'status', 'tenant']
    inlines = [SaleOrderItemInline, SaleOrderHistoryInline]

    fieldsets = (
        ('Informações Principais', {
            'fields': ('tenant', 'customer', 'salesperson', 'status')
        }),
        ('Valores Financeiros (calculados automaticamente)', {
            'classes': ('collapse',),
            'fields': ('subtotal_amount', 'discount_amount', 'shipping_amount', 'taxes_amount', 'total_amount')
        }),
        ('Envio e Pagamento', {
            'fields': ('payment_method', 'shipping_method', 'shipping_track')
        }),
        ('Observações', {
            'fields': ('customer_notes', 'internal_notes')
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at', 'deleted_at')
        }),
    )

    readonly_fields = (
        'subtotal_amount', 'discount_amount', 'shipping_amount',
        'taxes_amount', 'total_amount', 'created_at', 'updated_at', 'deleted_at'
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer', 'status', 'tenant')


@admin.register(SaleOrderItem)
class SaleOrderItemAdmin(admin.ModelAdmin):
    list_display = ('sale_order', 'product', 'quantity', 'unit_price', 'discount_amount', 'taxes_amount', 'total_amount')
    list_filter = ('sale_order__tenant',)
    search_fields = ('sale_order__id', 'product__name')
    autocomplete_fields = ['sale_order', 'product']
    readonly_fields = ('total_amount',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sale_order', 'product')
