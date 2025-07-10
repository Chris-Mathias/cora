from django.db import models
from django.conf import settings
from django.utils import timezone

from products.models import Product
from suppliers.models import Supplier
from tenants.models import Tenant


class PurchaseOrderStatus(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, blank=True, null=True, related_name='purchase_order_statuses')
    name = models.CharField(max_length=50)
    label = models.CharField(max_length=100)
    sequence_order = models.PositiveIntegerField(default=0)
    color_code = models.CharField(max_length=7, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Purchase Order Status'
        verbose_name_plural = 'Purchase Order Statuses'
        ordering = ['sequence_order', 'name']
        unique_together = ('tenant', 'name')

    def __str__(self):
        return self.name


class PurchaseOrder(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='purchase_orders')
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchase_orders')
    status = models.ForeignKey(PurchaseOrderStatus, on_delete=models.PROTECT, related_name='purchase_orders')
    expected_delivery_date = models.DateField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='created_purchase_orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Purchase Order'
        verbose_name_plural = 'Purchase Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f'Purchase Order #{self.id} - {self.supplier.name} ({self.status.name})'

    def soft_delete(self):
        try:
            deleted_status = PurchaseOrderStatus.objects.get(
                models.Q(tenant=self.tenant) | models.Q(tenant__isnull=True),
                name__iexact='DELETED'
            )
            self.status = deleted_status
        except PurchaseOrderStatus.DoesNotExist:
            pass

        self.deleted_at = timezone.now()
        self.save()


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='purchase_order_items')
    quantity = models.DecimalField(max_digits=10, decimal_places=3, default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Purchase Order Item'
        verbose_name_plural = 'Purchase Order Items'
        ordering = ['id']

    def __str__(self):
        return f'{self.quantity} x {self.product.name} (Order #{self.purchase_order.id})'
