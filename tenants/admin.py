from django.contrib import admin

from .models import Tenant, Role


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'is_active')
    search_fields = ('name', 'email')
    ordering = ('name',)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant')
    search_fields = ('name', 'tenant__name')
    ordering = ('name',)
