from django.db import models
from django.conf import settings
from django.utils import timezone

from locations.models import City
from tenants.models import Tenant


class Customer(models.Model):

    class CustomerType(models.TextChoices):
        INDIVIDUAL = 'PF', 'Pessoa Física'
        COMPANY = 'PJ', 'Pessoa Jurídica'

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='customers')
    salesperson = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='customers')
    type = models.CharField(max_length=2, choices=CustomerType.choices, default=CustomerType.INDIVIDUAL)
    name = models.CharField(max_length=255)
    trade_name = models.CharField(max_length=255, blank=True, null=True)
    cpf = models.CharField(max_length=14, blank=True, null=True)
    cnpj = models.CharField(max_length=18, blank=True, null=True)
    state_registration = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(null=True, blank=True)
    phone_primary = models.CharField(max_length=20, blank=True, null=True)
    phone_secondary = models.CharField(max_length=20, blank=True, null=True)
    address_street = models.CharField(max_length=255, blank=True, null=True)
    address_number = models.CharField(max_length=20, blank=True, null=True)
    addres_complement = models.CharField(max_length=100, blank=True, null=True)
    address_neighborhood = models.CharField(max_length=100, blank=True, null=True)
    address_postal_code = models.CharField(max_length=20, blank=True, null=True)
    address_city = models.ForeignKey(City, on_delete=models.SET_NULL, blank=True, null=True, related_name='customers')
    birth_date = models.DateField(blank=True, null=True)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
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
