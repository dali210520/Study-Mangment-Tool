"""
Admin configuration for deadlines app.
"""
from django.contrib import admin

from .models import Deadline


@admin.register(Deadline)
class DeadlineAdmin(admin.ModelAdmin):
    """Admin view for assignments, exams and other deadlines."""

    list_display = ('title', 'deadline_type', 'date', 'status', 'module', 'user')
    list_filter = ('deadline_type', 'status', 'date', 'created_at')
    search_fields = ('title', 'notes', 'module__name', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
