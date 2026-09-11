"""
Custom User Model for Study Management Tool.
Best Practice: Use custom user model from the start to allow future customizations.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re


class CustomUser(AbstractUser):
    """
    Custom User Model extending Django's AbstractUser.
    
    Additional fields:
    - email: Required, unique
    - bio: Optional biography
    - profile_picture_url: Optional URL to profile image (no Pillow dependency)
    - created_at: Timestamp of account creation
    - updated_at: Timestamp of last update
    - is_email_verified: Track email verification status
    """
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _('A user with that email already exists.'),
        }
    )
    bio = models.TextField(blank=True, null=True, max_length=500)
    profile_picture_url = models.TextField(
        blank=True,
        null=True,
        help_text='URL or base64 data to user profile picture'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_email_verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'auth_customuser'
        verbose_name = _('custom user')
        verbose_name_plural = _('custom users')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.email})"

    def clean(self):
        """Validate user data."""
        super().clean()
        # Email format validation
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, self.email):
            raise ValidationError({'email': _('Invalid email format.')})

    def save(self, *args, **kwargs):
        """Override save to ensure email is lowercase and clean is called."""
        self.email = self.email.lower()
        self.clean()
        super().save(*args, **kwargs)
