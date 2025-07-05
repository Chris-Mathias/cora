from django.conf import settings
from django.db import models

from products.models import Product
from sales.models import SaleOrder
from tenants.models import Tenant


class ProductionStage(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, blank=True, null=True, related_name='production_stages')
    name = models.CharField(max_length=100)
    sequence_order = models.PositiveIntegerField(default=0)
    color_code = models.CharField(max_length=7, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Production Stage'
        verbose_name_plural = 'Production Stages'
        ordering = ['sequence_order', 'name']
        unique_together = ('tenant', 'name')

    def __str__(self):
        return self.name


class ProductionOrder(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='production_orders')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='production_orders')
    sale_order = models.ForeignKey(SaleOrder, on_delete=models.SET_NULL, blank=True, null=True, related_name='production_orders')
    stage = models.ForeignKey(ProductionStage, on_delete=models.PROTECT, related_name='production_orders')
    quantity = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Production Order'
        verbose_name_plural = 'Production Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f'Production Order {self.id} - {self.product.name} ({self.quantity})'


class ProductionStageHistory(models.Model):
    production_order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, related_name='stage_histories')
    stage = models.ForeignKey(ProductionStage, on_delete=models.PROTECT, related_name='stage_histories')
    notes = models.TextField(blank=True, null=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='production_stage_histories')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Production Stage History'
        verbose_name_plural = 'Production Stage Histories'
        ordering = ['-created_at']

    def __str__(self):
        return f'History for Order #{self.production_order.id} - {self.stage.name} by {self.changed_by.name} on {self.created_at.strftime("%Y-%m-%d %H:%M:%S")}'
