from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from customers.models import Customer
from purchases.models import PurchaseOrder
from sales.models import SaleOrder
from suppliers.models import Supplier
from tenants.models import Tenant


class FinancialCategory(models.Model):

    class CategoryType(models.TextChoices):
        INCOME = 'IN', 'Receita'
        EXPENSE = 'EX', 'Despesa'

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='financial_categories')
    name = models.CharField(max_length=50)
    label = models.CharField(max_length=100)
    type = models.CharField(max_length=2, choices=CategoryType.choices, default=CategoryType.EXPENSE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Financial Category'
        verbose_name_plural = 'Financial Categories'
        unique_together = ('tenant', 'name')
        ordering = ['tenant', 'name']

    def __str__(self):
        return self.label


class FinancialStatus(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, blank=True, null=True, related_name='financial_statuses')
    name = models.CharField(max_length=50)
    label = models.CharField(max_length=100)
    color_code = models.CharField(max_length=7, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Financial Status'
        verbose_name_plural = 'Financial Statuses'
        unique_together = ('tenant', 'name')
        ordering = ['tenant', 'name']

    def __str__(self):
        return self.label


class CompanyAccount(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='company_accounts')
    account_name = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    agency_number = models.CharField(max_length=20, blank=True, null=True)
    account_number = models.CharField(max_length=30, blank=True, null=True)
    account_type = models.CharField(max_length=20, blank=True, null=True)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Company Account'
        verbose_name_plural = 'Company Accounts'
        unique_together = ('tenant', 'account_name')
        ordering = ['tenant', 'account_name']

    def __str__(self):
        return self.account_name


class AccountReceivable(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='accounts_receivable')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='accounts_receivable')
    sale_order = models.ForeignKey(SaleOrder, on_delete=models.SET_NULL, blank=True, null=True, related_name='accounts_receivable')
    status = models.ForeignKey(FinancialStatus, on_delete=models.PROTECT, related_name='accounts_receivable')
    category = models.ForeignKey(FinancialCategory, on_delete=models.PROTECT, related_name='accounts_receivable')
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Account Receivable'
        verbose_name_plural = 'Accounts Receivable'
        ordering = ['tenant', 'due_date']

    def __str__(self):
        return f"{self.customer} - {self.category.label} - {self.total_amount} ({self.status.label})"


class AccountPayable(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='accounts_payable')
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='accounts_payable')
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.SET_NULL, blank=True, null=True, related_name='accounts_payable')
    status = models.ForeignKey(FinancialStatus, on_delete=models.PROTECT, related_name='accounts_payable')
    category = models.ForeignKey(FinancialCategory, on_delete=models.PROTECT, related_name='accounts_payable')
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Account Payable'
        verbose_name_plural = 'Accounts Payable'
        ordering = ['tenant', 'due_date']

    def __str__(self):
        return f"{self.supplier} - {self.category.label} - {self.total_amount} ({self.status.label})"


class PaymentTransaction(models.Model):

    class PaymentMethod(models.TextChoices):
        CASH = 'CASH', 'Cash'
        CREDIT_CARD = 'CC', 'Credit Card'
        DEBIT_CARD = 'DC', 'Debit Card'
        BANK_TRANSFER = 'BT', 'Bank Transfer'
        PIX = 'PIX', 'Pix'
        CHECK = 'CHK', 'Check'
        OTHER = 'OTH', 'Other'

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='payment_transactions')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=5, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    company_account = models.ForeignKey(CompanyAccount, on_delete=models.PROTECT, related_name='payment_transactions')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    document_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='payment_transactions')
    document_object_id = models.PositiveIntegerField()
    document = GenericForeignKey('document_content_type', 'document_object_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Payment Transaction'
        verbose_name_plural = 'Payment Transactions'
        ordering = ['tenant', '-created_at']

    def __str__(self):
        return f"Transaction {self.id} - {self.amount_paid} ({self.payment_method})"


class CashFlow(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='cash_flows')
    category = models.ForeignKey(FinancialCategory, on_delete=models.PROTECT, related_name='cash_flows')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    payment = models.ForeignKey(PaymentTransaction, on_delete=models.CASCADE, related_name='cash_flows')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='cash_flows')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cash Flow'
        verbose_name_plural = 'Cash Flows'
        ordering = ['tenant', '-created_at']

    def __str__(self):
        return f"{self.description} - {self.amount} ({self.category.label})"
