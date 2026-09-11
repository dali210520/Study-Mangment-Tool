"""
Admin configuration for study plans app.
"""
from django.contrib import admin

from .models import StudyPlanEntry


@admin.register(StudyPlanEntry)
class StudyPlanEntryAdmin(admin.ModelAdmin):
    """Admin view for study plan entries."""

    list_display = ('topic', 'planned_date', 'duration_minutes', 'status', 'module', 'deadline', 'user')
    list_filter = ('status', 'planned_date', 'created_at')
    search_fields = ('topic', 'notes', 'module__name', 'deadline__title', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
