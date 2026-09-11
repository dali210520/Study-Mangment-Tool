"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser


class CustomUserAdmin(BaseUserAdmin):
    """Custom User Admin."""
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('bio', 'profile_picture_url', 'is_email_verified', 'created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_email_verified', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)


admin.site.register(CustomUser, CustomUserAdmin)
