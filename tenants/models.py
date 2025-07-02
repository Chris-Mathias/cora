from django.db import models
from django.conf import settings
from django.contrib.auth.models import Permission
from django.utils import timezone

from locations.models import City


class Tenant(models.Model):

    class TenantType(models.TextChoices):
        INDIVIDUAL = 'PF', 'Pessoa Física'
        COMPANY = 'PJ', 'Pessoa Jurídica'

    type = models.CharField(max_length=2, choices=TenantType.choices, default=TenantType.INDIVIDUAL)
    name = models.CharField(max_length=255)
    trade_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_primary = models.CharField(max_length=20, blank=True, null=True)
    phone_secondary = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    cpf = models.CharField(max_length=14, blank=True, null=True)
    cnpj = models.CharField(max_length=17, blank=True, null=True)
    state_registration = models.CharField(max_length=30, blank=True, null=True)
    address_street = models.CharField(max_length=255, blank=True, null=True)
    address_number = models.CharField(max_length=20, blank=True, null=True)
    addres_complement = models.CharField(max_length=100, blank=True, null=True)
    address_neighborhood = models.CharField(max_length=100, blank=True, null=True)
    address_postal_code = models.CharField(max_length=20, blank=True, null=True)
    address_city = models.ForeignKey(City, on_delete=models.SET_NULL, blank=True, null=True, related_name='tenants')
    subdomain = models.CharField(max_length=100, unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='TenantUser', blank=True, related_name='tenants')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Tenant'
        verbose_name_plural = 'Tenants'
        ordering = ['name']

    def __str__(self):
        return self.name or self.trade_name

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()

    def restore(self):
        self.deleted_at = None
        self.is_active = True
        self.save()


class Role(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="roles", null=True, blank=True)
    name = models.CharField(max_length=50)
    label = models.CharField(max_length=100)
    permissions = models.ManyToManyField(Permission, related_name='roles', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ['tenant', 'name']
        constraints = [
            models.UniqueConstraint(fields=['tenant', 'name'], name='unique_tenant_role'),
            models.UniqueConstraint(fields=['name'], condition=models.Q(tenant__isnull=True), name='unique_global_role')
        ]

    def __str__(self):
        if self.tenant:
            return f"{self.label} ({self.tenant.name})"
        return f"{self.label} (Global Role)"


class TenantUser(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tenant User'
        verbose_name_plural = 'Tenant Users'
        unique_together = ('tenant', 'user')
        ordering = ['tenant', 'user']

    def __str__(self):
        return f"{self.user.email} @ {self.tenant.name} ({self.role.name})"
