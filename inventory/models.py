from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from products.models import Product
from purchases.models import PurchaseOrder
from suppliers.models import Supplier
from tenants.models import Tenant


class StockEntry(models.Model):

    class StockEntryStatus(models.TextChoices):
        DRAFT = 'DR', 'Rascunho'
        COMPLETED = 'CO', 'Concluído'

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='stock_entries')
    purchase = models.ForeignKey(PurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_entries')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_entries')
    status = models.CharField(max_length=2, choices=StockEntryStatus.choices, default=StockEntryStatus.DRAFT)
    notes = models.TextField(blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_entries')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Stock Entry'
        verbose_name_plural = 'Stock Entries'
        ordering = ['-created_at']

    def __str__(self):
        return f'Stock Entry {self.id}'


class StockEntryItem(models.Model):
    stock_entry = models.ForeignKey(StockEntry, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_entry_items')
    quantity = models.DecimalField(max_digits=10, decimal_places=3, default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    expiration_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Stock Entry Item'
        verbose_name_plural = 'Stock Entry Items'

    def __str__(self):
        return f'{self.quantity} x {self.product.name} (Entry #{self.stock_entry.id})'


class StockMovement(models.Model):

    class MovementDirection(models.TextChoices):
        IN = 'IN', 'Entrada'
        OUT = 'OUT', 'Saída'

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='stock_movements')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='stock_movements')
    direction = models.CharField(max_length=3, choices=MovementDirection.choices, default=MovementDirection.IN)
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    new_stock = models.DecimalField(max_digits=10, decimal_places=3)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    source_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    source_object_id = models.PositiveIntegerField()
    source_document = GenericForeignKey('source_content_type', 'source_object_id')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_movements')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Stock Movement'
        verbose_name_plural = 'Stock Movements'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_direction_display()} {self.quantity} x {self.product.name} (Movement #{self.id})'


class StockAdjustmentType(models.Model):

    class Direction(models.TextChoices):
        INCREASE = 'IN', 'Aumento'
        DECREASE = 'OUT', 'Redução'

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, blank=True, null=True, related_name='stock_adjustment_types')
    name = models.CharField(max_length=50)
    label = models.CharField(max_length=100)
    direction = models.CharField(max_length=3, choices=Direction.choices, default=Direction.DECREASE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Stock Adjustment Type'
        verbose_name_plural = 'Stock Adjustment Types'
        unique_together = ('tenant', 'name')
        ordering = ['name']

    def __str__(self):
        return f'{self.label} ({self.get_direction_display()})'


class StockAdjustment(models.Model):

    class StockAdjustmentStatus(models.TextChoices):
        DRAFT = 'DR', 'Rascunho'
        COMPLETED = 'CO', 'Concluído'

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='stock_adjustments')
    status = models.CharField(max_length=2, choices=StockAdjustmentStatus.choices, default=StockAdjustmentStatus.DRAFT)
    notes = models.TextField(blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_adjustments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Stock Adjustment'
        verbose_name_plural = 'Stock Adjustments'
        ordering = ['-created_at']

    def __str__(self):
        return f'Stock Adjustment {self.id} - {self.get_status_display()}'


class StockAdjustmentItem(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='stock_adjustment_items')
    stock_adjustment = models.ForeignKey(StockAdjustment, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='stock_adjustment_items')
    adjustment_type = models.ForeignKey(StockAdjustmentType, on_delete=models.PROTECT, related_name='stock_adjustment_items')
    quantity = models.DecimalField(max_digits=10, decimal_places=3, default=1)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Stock Adjustment Item'
        verbose_name_plural = 'Stock Adjustment Items'
        ordering = ['id']

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'
