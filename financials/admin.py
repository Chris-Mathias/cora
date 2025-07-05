from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import (AccountPayable, AccountReceivable, CashFlow,
                     CompanyAccount, FinancialCategory, FinancialStatus,
                     PaymentTransaction)


class PaymentTransactionInline(GenericTabularInline):
    model = PaymentTransaction
    extra = 0
    fields = ('amount_paid', 'payment_method', 'company_account', 'transaction_id', 'created_at')
    readonly_fields = ('created_at',)
    autocomplete_fields = ['company_account']
    ct_field = "document_content_type"
    ct_fk_field = "document_object_id"


@admin.register(FinancialCategory)
class FinancialCategoryAdmin(admin.ModelAdmin):
    list_display = ('label', 'name', 'type', 'tenant')
    list_filter = ('type', 'tenant')
    search_fields = ('name', 'label')


@admin.register(FinancialStatus)
class FinancialStatusAdmin(admin.ModelAdmin):
    list_display = ('label', 'name', 'color_code', 'tenant')
    list_filter = ('tenant',)
    search_fields = ('name', 'label')


@admin.register(CompanyAccount)
class CompanyAccountAdmin(admin.ModelAdmin):
    list_display = ('account_name', 'bank_name', 'current_balance', 'is_active', 'tenant')
    list_filter = ('is_active', 'tenant')
    search_fields = ('account_name', 'bank_name')
    readonly_fields = ('current_balance',)


@admin.register(AccountReceivable)
class AccountReceivableAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'due_date', 'total_amount', 'amount_paid', 'status')
    list_filter = ('status', 'due_date', 'tenant')
    search_fields = ('id', 'customer__name', 'description')
    autocomplete_fields = ['tenant', 'customer', 'sale_order', 'status']
    readonly_fields = ('amount_paid', 'payment_date', 'created_at', 'updated_at')
    inlines = [PaymentTransactionInline]
    fieldsets = (
        ('Informações Principais', {
            'fields': ('tenant', 'customer', 'sale_order', 'status', 'description')
        }),
        ('Valores', {
            'fields': ('total_amount', 'amount_paid', 'due_date', 'payment_date')
        }),
    )


@admin.register(AccountPayable)
class AccountPayableAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'due_date', 'total_amount', 'amount_paid', 'status')
    list_filter = ('status', 'due_date', 'tenant')
    search_fields = ('id', 'supplier__name', 'description')
    autocomplete_fields = ['tenant', 'supplier', 'purchase_order', 'status']
    readonly_fields = ('amount_paid', 'payment_date', 'created_at', 'updated_at')
    inlines = [PaymentTransactionInline]
    fieldsets = (
        ('Informações Principais', {
            'fields': ('tenant', 'supplier', 'purchase_order', 'status', 'description')
        }),
        ('Valores', {
            'fields': ('total_amount', 'amount_paid', 'due_date', 'payment_date')
        }),
    )


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'amount_paid', 'payment_method', 'company_account', 'created_at')
    list_filter = ('payment_method', 'tenant')
    search_fields = ('transaction_id',)
    autocomplete_fields = ['tenant', 'company_account']
    readonly_fields = [f.name for f in PaymentTransaction._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CashFlow)
class CashFlowAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'category', 'amount', 'description', 'payment')
    list_filter = ('category', 'tenant', 'created_at')
    search_fields = ('description',)
    readonly_fields = [f.name for f in CashFlow._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
