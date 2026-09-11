"""
Models for study modules and lectures.
"""
from django.conf import settings
from django.db import models


class StudyModule(models.Model):
    """
    A university module or course owned by one user.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='study_modules',
    )
    name = models.CharField(max_length=120)
    semester = models.CharField(max_length=50, blank=True)
    lecturer = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        if self.semester:
            return f'{self.name} ({self.semester})'
        return self.name


class Lecture(models.Model):
    """
    A lecture session or course unit belonging to a study module.
    """

    module = models.ForeignKey(
        StudyModule,
        on_delete=models.CASCADE,
        related_name='lectures',
    )
    title = models.CharField(max_length=150)
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'title']

    def __str__(self):
        return f'{self.date} - {self.title}'
