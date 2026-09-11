"""
Tests for study plan models.
"""
from datetime import date

import pytest
from django.core.exceptions import ValidationError

from apps.accounts.models import CustomUser
from apps.courses.models import StudyModule
from apps.deadlines.models import Deadline
from apps.plans.models import StudyPlanEntry


@pytest.mark.django_db
@pytest.mark.unit
class TestStudyPlanEntryModel:
    """Test cases for the StudyPlanEntry model."""

    def test_study_plan_entry_str(self, authenticated_user):
        entry = StudyPlanEntry.objects.create(
            user=authenticated_user,
            topic='Recursion practice',
            planned_date=date(2026, 10, 12),
        )

        assert str(entry) == '2026-10-12 - Recursion practice'

    def test_default_duration_and_status(self, authenticated_user):
        entry = StudyPlanEntry.objects.create(
            user=authenticated_user,
            topic='Read lecture notes',
            planned_date=date(2026, 10, 13),
        )

        assert entry.duration_minutes == 60
        assert entry.status == StudyPlanEntry.Status.PLANNED

    def test_entry_can_reference_own_module_and_deadline(self, authenticated_user):
        module = StudyModule.objects.create(user=authenticated_user, name='Algorithms')
        deadline = Deadline.objects.create(
            user=authenticated_user,
            module=module,
            title='Algorithms exam',
            date=date(2026, 12, 12),
        )

        entry = StudyPlanEntry.objects.create(
            user=authenticated_user,
            module=module,
            deadline=deadline,
            topic='Graph algorithms',
            planned_date=date(2026, 11, 20),
        )

        assert entry.module == module
        assert entry.deadline == deadline

    def test_entry_module_must_belong_to_same_user(self, authenticated_user):
        other_user = CustomUser.objects.create_user(
            username='planmoduleowner',
            email='planmoduleowner@example.com',
            password='SecurePass123!',
        )
        module = StudyModule.objects.create(user=other_user, name='Private Module')

        with pytest.raises(ValidationError):
            StudyPlanEntry.objects.create(
                user=authenticated_user,
                module=module,
                topic='Invalid module plan',
                planned_date=date(2026, 11, 20),
            )

    def test_entry_deadline_must_belong_to_same_user(self, authenticated_user):
        other_user = CustomUser.objects.create_user(
            username='plandeadlineowner',
            email='plandeadlineowner@example.com',
            password='SecurePass123!',
        )
        deadline = Deadline.objects.create(
            user=other_user,
            title='Private deadline',
            date=date(2026, 12, 12),
        )

        with pytest.raises(ValidationError):
            StudyPlanEntry.objects.create(
                user=authenticated_user,
                deadline=deadline,
                topic='Invalid deadline plan',
                planned_date=date(2026, 11, 20),
            )
