from django.contrib import admin

from .models import ProductionOrder, ProductionStage, ProductionStageHistory


class ProductionStageHistoryInline(admin.TabularInline):
    model = ProductionStageHistory
    extra = 0
    readonly_fields = ('stage', 'changed_by', 'notes', 'created_at')
    can_delete = False
    verbose_name = "Histórico de Etapa"
    verbose_name_plural = "Históricos de Etapa"

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ProductionStage)
class ProductionStageAdmin(admin.ModelAdmin):
    list_display = ('label', 'name', 'sequence_order', 'tenant')
    list_filter = ('tenant',)
    search_fields = ('name',)


@admin.register(ProductionOrder)
class ProductionOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'quantity', 'stage', 'created_at', 'tenant')
    list_filter = ('stage', 'tenant', 'created_at')
    search_fields = ('id', 'product__name', 'sale_order__id')
    autocomplete_fields = ['product', 'sale_order', 'stage', 'tenant']
    inlines = [ProductionStageHistoryInline]

    fieldsets = (
        ('Informações Principais', {
            'fields': ('tenant', 'product', 'quantity', 'stage')
        }),
        ('Vínculos', {
            'classes': ('collapse',),
            'fields': ('sale_order',)
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'stage', 'tenant', 'sale_order')
