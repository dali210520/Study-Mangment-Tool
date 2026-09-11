"""
Models for uploaded study materials.
"""
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.courses.models import StudyModule


def material_upload_path(instance, filename):
    """Store uploaded PDFs below a user/module specific path."""
    return f'study_materials/user_{instance.user_id}/module_{instance.module_id}/{filename}'


class StudyMaterial(models.Model):
    """
    A PDF study material uploaded by a user for one module.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='study_materials',
    )
    module = models.ForeignKey(
        StudyModule,
        on_delete=models.CASCADE,
        related_name='study_materials',
    )
    title = models.CharField(max_length=150)
    file = models.FileField(upload_to=material_upload_path)
    original_filename = models.CharField(max_length=255)
    extracted_text = models.TextField(blank=True)
    page_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def clean(self):
        """Ensure materials reference an owned module and use a PDF file."""
        super().clean()
        if self.module_id and self.user_id and self.module.user_id != self.user_id:
            raise ValidationError({'module': 'Module must belong to the material owner.'})

        filename = self.original_filename or getattr(self.file, 'name', '')
        if filename and Path(filename).suffix.lower() != '.pdf':
            raise ValidationError({'file': 'Only PDF files are supported.'})

    def save(self, *args, **kwargs):
        """Validate before saving."""
        self.clean()
        super().save(*args, **kwargs)
