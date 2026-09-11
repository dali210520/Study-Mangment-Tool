"""
Admin configuration for courses app.
"""
from django.contrib import admin

from .models import Lecture, StudyModule


class LectureInline(admin.TabularInline):
    """Show lectures directly on a module in Django admin."""

    model = Lecture
    extra = 0


@admin.register(StudyModule)
class StudyModuleAdmin(admin.ModelAdmin):
    """Admin view for study modules."""

    list_display = ('name', 'semester', 'lecturer', 'user', 'created_at')
    list_filter = ('semester', 'created_at')
    search_fields = ('name', 'lecturer', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [LectureInline]


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    """Admin view for lectures."""

    list_display = ('title', 'module', 'date', 'created_at')
    list_filter = ('date', 'created_at')
    search_fields = ('title', 'module__name', 'notes')
    readonly_fields = ('created_at', 'updated_at')
