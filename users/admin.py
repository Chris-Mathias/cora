from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'phone_primary', 'is_active', 'is_staff', 'created_at', 'updated_at')
    search_fields = ('email', 'name')
    list_filter = ('is_active', 'is_staff')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted_at__isnull=True)
