"""
Models for study planning.
"""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.courses.models import StudyModule
from apps.deadlines.models import Deadline


class StudyPlanEntry(models.Model):
    """
    A planned learning session owned by one user.
    """

    class Status(models.TextChoices):
        PLANNED = 'planned', 'Planned'
        IN_PROGRESS = 'in_progress', 'In progress'
        DONE = 'done', 'Done'
        SKIPPED = 'skipped', 'Skipped'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='study_plan_entries',
    )
    module = models.ForeignKey(
        StudyModule,
        on_delete=models.SET_NULL,
        related_name='study_plan_entries',
        blank=True,
        null=True,
    )
    deadline = models.ForeignKey(
        Deadline,
        on_delete=models.SET_NULL,
        related_name='study_plan_entries',
        blank=True,
        null=True,
    )
    topic = models.CharField(max_length=150)
    planned_date = models.DateField()
    duration_minutes = models.PositiveIntegerField(default=60)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['planned_date', 'topic']

    def __str__(self):
        return f'{self.planned_date} - {self.topic}'

    def clean(self):
        """Ensure linked objects belong to the same user as the plan entry."""
        super().clean()
        if self.module_id and self.user_id and self.module.user_id != self.user_id:
            raise ValidationError({'module': 'Module must belong to the plan owner.'})
        if self.deadline_id and self.user_id and self.deadline.user_id != self.user_id:
            raise ValidationError({'deadline': 'Deadline must belong to the plan owner.'})

    def save(self, *args, **kwargs):
        """Validate ownership before saving."""
        self.clean()
        super().save(*args, **kwargs)
