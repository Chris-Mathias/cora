from django.contrib import admin

from .models import Product, ProductCategory, ProductBrand, Attribute, AttributeValue, ProductComposition, ProductAttributeValue


class ProductCompositionInline(admin.TabularInline):
    model = ProductComposition
    fk_name = 'product'
    extra = 1
    verbose_name = 'Product Composition'
    verbose_name_plural = 'Product Compositions'
    autocomplete_fields = ['component']


class ProductAttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue
    extra = 1
    verbose_name = 'Product Attribute Value'
    verbose_name_plural = 'Product Attribute Values'
    autocomplete_fields = ['attribute_value']


class VariantInline(admin.TabularInline):
    model = Product
    fk_name = 'parent'
    extra = 1
    verbose_name = 'Variant'
    verbose_name_plural = 'Variants'
    fields = ('name', 'price', 'sku', 'stock_quantity')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'price', 'created_at', 'updated_at')
    search_fields = ('name', 'category__name', 'brand__name')
    list_filter = ('category', 'brand')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 20
    autocomplete_fields = ['parent', 'category', 'brand']

    fieldsets = (
        (None, {
            'fields': ('tenant', 'name', 'sku', 'description')
        }),
        ('Type & Relationships', {
            'fields': ('parent', 'category', 'brand', 'is_variant', 'is_composite', 'is_active')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'avg_cost_price', 'stock_quantity', 'minimum_stock_quantity', 'unit_of_measure')
        }),
    )

    def get_inlines(self, request, obj=None):
        inlines = []
        if obj:
            if obj.is_variant:
                inlines.append(ProductAttributeValueInline)
            if obj.is_composite:
                inlines.append(ProductCompositionInline)
            if not obj.is_variant and not obj.is_composite:
                inlines.append(VariantInline)
        return inlines

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent', 'category', 'brand', 'tenant')


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('tenant',)
    ordering = ('name',)
    date_hierarchy = 'created_at'
    list_per_page = 20


@admin.register(ProductBrand)
class ProductBrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('tenant',)
    ordering = ('name',)
    date_hierarchy = 'created_at'
    list_per_page = 20


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('tenant',)
    ordering = ('name',)
    date_hierarchy = 'created_at'
    list_per_page = 20


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('attribute', 'value', 'tenant', 'created_at', 'updated_at')
    search_fields = ('attribute__name', 'value')
    list_filter = ('tenant', 'attribute')
    ordering = ('attribute__name', 'value')
    date_hierarchy = 'created_at'
    list_per_page = 20
