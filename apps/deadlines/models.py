"""
Models for assignments, exams and other academic deadlines.
"""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.courses.models import StudyModule


class Deadline(models.Model):
    """
    A user-owned academic deadline such as an exam or assignment.
    """

    class DeadlineType(models.TextChoices):
        ASSIGNMENT = 'assignment', 'Assignment'
        EXAM = 'exam', 'Exam'
        PRESENTATION = 'presentation', 'Presentation'
        PROJECT = 'project', 'Project'
        OTHER = 'other', 'Other'

    class Status(models.TextChoices):
        UPCOMING = 'upcoming', 'Upcoming'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='deadlines',
    )
    module = models.ForeignKey(
        StudyModule,
        on_delete=models.SET_NULL,
        related_name='deadlines',
        blank=True,
        null=True,
    )
    title = models.CharField(max_length=150)
    deadline_type = models.CharField(
        max_length=20,
        choices=DeadlineType.choices,
        default=DeadlineType.ASSIGNMENT,
    )
    date = models.DateField()
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UPCOMING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'title']

    def __str__(self):
        return f'{self.title} ({self.get_deadline_type_display()})'

    def clean(self):
        """Ensure deadlines can only reference modules owned by the same user."""
        super().clean()
        if self.module_id and self.user_id and self.module.user_id != self.user_id:
            raise ValidationError({'module': 'Module must belong to the deadline owner.'})

    def save(self, *args, **kwargs):
        """Validate ownership before saving."""
        self.clean()
        super().save(*args, **kwargs)
