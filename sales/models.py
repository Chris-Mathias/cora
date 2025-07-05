from django.conf import settings
from django.db import models
from django.utils import timezone

from customers.models import Customer
from products.models import Product
from tenants.models import Tenant


class SaleOrderStatus(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, blank=True, null=True, related_name='sale_order_statuses')
    name = models.CharField(max_length=50)
    label = models.CharField(max_length=100)
    sequence_order = models.PositiveIntegerField(default=0)
    color_code = models.CharField(max_length=7, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sale Order Status'
        verbose_name_plural = 'Sale Order Statuses'
        ordering = ['sequence_order', 'name']
        unique_together = ('tenant', 'name')

    def __str__(self):
        return self.name


class SaleOrder(models.Model):

    class PaymentMethod(models.TextChoices):
        CASH = 'CASH', 'Cash'
        CREDIT_CARD = 'CC', 'Credit Card'
        DEBIT_CARD = 'DC', 'Debit Card'
        BANK_TRANSFER = 'BT', 'Bank Transfer'
        PIX = 'PIX', 'Pix'
        CHECK = 'CHK', 'Check'
        OTHER = 'OTH', 'Other'

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='sale_orders')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='sale_orders')
    salesperson = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, blank=True, null=True, related_name='sale_orders')
    status = models.ForeignKey(SaleOrderStatus, on_delete=models.PROTECT, related_name='sale_orders', blank=True, null=True)
    subtotal_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    taxes_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=5, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    shipping_method = models.CharField(max_length=100, blank=True, null=True)
    shipping_track = models.CharField(max_length=100, blank=True, null=True)
    customer_notes = models.TextField(blank=True, null=True)
    internal_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Sale Order'
        verbose_name_plural = 'Sale Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f'Sale Order #{self.id} - {self.customer.name}'

    def soft_delete(self):
        try:
            deleted_status = SaleOrderStatus.objects.get(
                models.Q(tenant=self.tenant) | models.Q(tenant__isnull=True),
                name__iexact='DELETED'
            )
            self.status = deleted_status
        except SaleOrderStatus.DoesNotExist:
            pass

        self.deleted_at = timezone.now()
        self.save()


class SaleOrderItem(models.Model):
    sale_order = models.ForeignKey(SaleOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='sale_order_items')
    quantity = models.DecimalField(max_digits=10, decimal_places=3, default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    taxes_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sale Order Item'
        verbose_name_plural = 'Sale Order Items'
        ordering = ['id']

    def __str__(self):
        return f'{self.quantity} x {self.product.name} (Order #{self.sale_order.id})'


class SaleOrderHistory(models.Model):
    sale_order = models.ForeignKey(SaleOrder, on_delete=models.CASCADE, related_name='history')
    status = models.ForeignKey(SaleOrderStatus, on_delete=models.PROTECT, related_name='order_history')
    notes = models.TextField(blank=True, null=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='sale_order_history')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sale Order History'
        verbose_name_plural = 'Sale Order Histories'
        ordering = ['-created_at']

    def __str__(self):
        return f'History for Order #{self.sale_order.id} - {self.status.name} by {self.changed_by.name} on {self.created_at.strftime("%Y-%m-%d %H:%M:%S")}'
