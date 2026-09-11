"""
Models for student task management.
"""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.courses.models import StudyModule


class Task(models.Model):
    """
    A study task owned by one user and optionally connected to a module.
    """

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In progress'
        DONE = 'done', 'Done'

    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks',
    )
    module = models.ForeignKey(
        StudyModule,
        on_delete=models.SET_NULL,
        related_name='tasks',
        blank=True,
        null=True,
    )
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    due_date = models.DateField(blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['status', 'due_date', '-created_at']

    def __str__(self):
        return self.title

    def clean(self):
        """Ensure users can only connect tasks to their own modules."""
        super().clean()
        if self.module_id and self.user_id and self.module.user_id != self.user_id:
            raise ValidationError({'module': 'Module must belong to the task owner.'})

    def save(self, *args, **kwargs):
        """Keep completed_at in sync with the task status."""
        if self.status == self.Status.DONE and self.completed_at is None:
            self.completed_at = timezone.now()
        if self.status != self.Status.DONE:
            self.completed_at = None
        self.clean()
        super().save(*args, **kwargs)
