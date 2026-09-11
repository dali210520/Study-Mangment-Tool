"""
Admin configuration for study materials app.
"""
from django.contrib import admin

from .models import StudyMaterial


@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    """Admin view for uploaded study materials."""

    list_display = ('title', 'module', 'user', 'page_count', 'created_at')
    list_filter = ('created_at', 'module')
    search_fields = ('title', 'original_filename', 'module__name', 'user__username')
    readonly_fields = ('extracted_text', 'page_count', 'created_at', 'updated_at')
