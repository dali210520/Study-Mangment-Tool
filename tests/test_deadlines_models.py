"""
Tests for deadline-related models.
"""
from datetime import date

import pytest
from django.core.exceptions import ValidationError

from apps.accounts.models import CustomUser
from apps.courses.models import StudyModule
from apps.deadlines.models import Deadline


@pytest.mark.django_db
@pytest.mark.unit
class TestDeadlineModel:
    """Test cases for the Deadline model."""

    def test_deadline_str(self, authenticated_user):
        deadline = Deadline.objects.create(
            user=authenticated_user,
            title='Final exam',
            deadline_type=Deadline.DeadlineType.EXAM,
            date=date(2026, 12, 15),
        )

        assert str(deadline) == 'Final exam (Exam)'

    def test_default_type_and_status(self, authenticated_user):
        deadline = Deadline.objects.create(
            user=authenticated_user,
            title='Essay submission',
            date=date(2026, 11, 1),
        )

        assert deadline.deadline_type == Deadline.DeadlineType.ASSIGNMENT
        assert deadline.status == Deadline.Status.UPCOMING

    def test_deadline_can_reference_own_module(self, authenticated_user):
        module = StudyModule.objects.create(
            user=authenticated_user,
            name='Databases',
        )

        deadline = Deadline.objects.create(
            user=authenticated_user,
            module=module,
            title='SQL project',
            date=date(2026, 11, 10),
        )

        assert deadline.module == module

    def test_deadline_module_must_belong_to_same_user(self, authenticated_user):
        other_user = CustomUser.objects.create_user(
            username='deadlineowner',
            email='deadlineowner@example.com',
            password='SecurePass123!',
        )
        module = StudyModule.objects.create(
            user=other_user,
            name='Private Module',
        )

        with pytest.raises(ValidationError):
            Deadline.objects.create(
                user=authenticated_user,
                module=module,
                title='Invalid deadline',
                date=date(2026, 11, 10),
            )
