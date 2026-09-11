"""
Apps configuration for overview.
"""
from django.apps import AppConfig


class OverviewConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.overview'
    verbose_name = 'Overview & Analytics'
