"""
Tests for task management models.
"""
import pytest
from django.core.exceptions import ValidationError

from apps.accounts.models import CustomUser
from apps.courses.models import StudyModule
from apps.tasks.models import Task


@pytest.mark.django_db
@pytest.mark.unit
class TestTaskModel:
    """Test cases for the Task model."""

    def test_task_str(self, authenticated_user):
        task = Task.objects.create(
            user=authenticated_user,
            title='Read chapter 1',
        )

        assert str(task) == 'Read chapter 1'

    def test_done_status_sets_completed_at(self, authenticated_user):
        task = Task.objects.create(
            user=authenticated_user,
            title='Submit exercise',
            status=Task.Status.DONE,
        )

        assert task.completed_at is not None

    def test_reopening_task_clears_completed_at(self, authenticated_user):
        task = Task.objects.create(
            user=authenticated_user,
            title='Prepare slides',
            status=Task.Status.DONE,
        )

        task.status = Task.Status.OPEN
        task.save()

        assert task.completed_at is None

    def test_task_module_must_belong_to_same_user(self, authenticated_user):
        other_user = CustomUser.objects.create_user(
            username='taskmoduleowner',
            email='taskmoduleowner@example.com',
            password='SecurePass123!',
        )
        module = StudyModule.objects.create(
            user=other_user,
            name='Private Module',
        )

        with pytest.raises(ValidationError):
            Task.objects.create(
                user=authenticated_user,
                module=module,
                title='Invalid module task',
            )
