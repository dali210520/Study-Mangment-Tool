"""
Admin configuration for tasks app.
"""
from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin view for student tasks."""

    list_display = ('title', 'user', 'module', 'status', 'priority', 'due_date')
    list_filter = ('status', 'priority', 'due_date', 'created_at')
    search_fields = ('title', 'description', 'user__username', 'module__name')
    readonly_fields = ('completed_at', 'created_at', 'updated_at')
