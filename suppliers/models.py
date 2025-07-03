from django.db import models
from django.utils import timezone

from locations.models import City
from tenants.models import Tenant


class Supplier(models.Model):

    class SupplierType(models.TextChoices):
        INDIVIDUAL = 'PF', 'Pessoa Física'
        COMPANY = 'PJ', 'Pessoa Jurídica'

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='suppliers')
    type = models.CharField(max_length=2, choices=SupplierType.choices, default=SupplierType.COMPANY)
    name = models.CharField(max_length=255)
    trade_name = models.CharField(max_length=255, blank=True, null=True)
    cpf = models.CharField(max_length=14, blank=True, null=True)
    cnpj = models.CharField(max_length=18, blank=True, null=True)
    state_registration = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(null=True, blank=True)
    phone_primary = models.CharField(max_length=20, blank=True, null=True)
    phone_secondary = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    contact_person_name = models.CharField(max_length=255, blank=True, null=True)
    lead_time_days = models.PositiveIntegerField(blank=True, null=True)
    address_street = models.CharField(max_length=255, blank=True, null=True)
    address_number = models.CharField(max_length=20, blank=True, null=True)
    address_complement = models.CharField(max_length=100, blank=True, null=True)
    address_neighborhood = models.CharField(max_length=100, blank=True, null=True)
    address_postal_code = models.CharField(max_length=20, blank=True, null=True)
    address_city = models.ForeignKey(City, on_delete=models.SET_NULL, blank=True, null=True, related_name='suppliers')
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.tenant.name})'

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()

    def restore(self):
        self.deleted_at = None
        self.is_active = True
        self.save()
