"""
Tests for task management API endpoints.
"""
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import CustomUser
from apps.courses.models import StudyModule
from apps.tasks.models import Task


@pytest.fixture
def api_client():
    """Fixture providing a DRF API client."""
    return APIClient()


@pytest.fixture
def task_module(authenticated_user):
    """Fixture providing a module for task tests."""
    return StudyModule.objects.create(
        user=authenticated_user,
        name='Algorithms',
        semester='WS 2026',
    )


@pytest.fixture
def study_task(authenticated_user, task_module):
    """Fixture providing a task owned by the authenticated user."""
    return Task.objects.create(
        user=authenticated_user,
        module=task_module,
        title='Solve exercise sheet',
        due_date='2026-10-31',
        priority=Task.Priority.HIGH,
    )


@pytest.mark.django_db
@pytest.mark.integration
class TestTaskAPI:
    """API tests for tasks."""

    def test_task_list_requires_authentication(self, api_client):
        response = api_client.get(reverse('task-list'))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_task_for_authenticated_user(self, api_client, authenticated_user, task_module):
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.post(
            reverse('task-list'),
            {
                'module': task_module.id,
                'title': 'Read lecture notes',
                'description': 'Focus on chapter 2.',
                'due_date': '2026-10-20',
                'priority': Task.Priority.MEDIUM,
            },
            format='json',
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Read lecture notes'
        assert response.data['module'] == task_module.id
        assert response.data['module_name'] == task_module.name
        assert response.data['status'] == Task.Status.OPEN
        assert Task.objects.filter(user=authenticated_user, title='Read lecture notes').exists()

    def test_create_task_without_module(self, api_client, authenticated_user):
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.post(
            reverse('task-list'),
            {'title': 'Buy notebooks'},
            format='json',
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['module'] is None
        assert response.data['priority'] == Task.Priority.MEDIUM

    def test_create_task_rejects_other_users_module(self, api_client, authenticated_user):
        other_user = CustomUser.objects.create_user(
            username='othertaskuser',
            email='othertaskuser@example.com',
            password='SecurePass123!',
        )
        other_module = StudyModule.objects.create(
            user=other_user,
            name='Private Module',
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.post(
            reverse('task-list'),
            {'module': other_module.id, 'title': 'Invalid task'},
            format='json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not Task.objects.filter(title='Invalid task').exists()

    def test_list_only_returns_own_tasks(self, api_client, authenticated_user):
        other_user = CustomUser.objects.create_user(
            username='othertaskowner',
            email='othertaskowner@example.com',
            password='SecurePass123!',
        )
        own_task = Task.objects.create(
            user=authenticated_user,
            title='Own task',
        )
        Task.objects.create(
            user=other_user,
            title='Other task',
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(reverse('task-list'))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == own_task.id

    def test_filter_tasks_by_status_priority_module_and_due_date(
        self,
        api_client,
        authenticated_user,
        task_module,
    ):
        matching_task = Task.objects.create(
            user=authenticated_user,
            module=task_module,
            title='Matching task',
            due_date='2026-10-20',
            priority=Task.Priority.HIGH,
            status=Task.Status.IN_PROGRESS,
        )
        Task.objects.create(
            user=authenticated_user,
            module=task_module,
            title='Wrong priority',
            due_date='2026-10-20',
            priority=Task.Priority.LOW,
            status=Task.Status.IN_PROGRESS,
        )
        Task.objects.create(
            user=authenticated_user,
            title='Wrong due date',
            due_date='2026-12-01',
            priority=Task.Priority.HIGH,
            status=Task.Status.IN_PROGRESS,
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(
            reverse('task-list'),
            {
                'status': Task.Status.IN_PROGRESS,
                'priority': Task.Priority.HIGH,
                'module': task_module.id,
                'due_before': '2026-10-31',
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert [task['id'] for task in response.data] == [matching_task.id]

    def test_search_and_order_tasks_by_priority(self, api_client, authenticated_user, task_module):
        Task.objects.create(
            user=authenticated_user,
            module=task_module,
            title='Read sorting notes',
            description='Prepare examples.',
            due_date='2026-10-20',
            priority=Task.Priority.LOW,
        )
        Task.objects.create(
            user=authenticated_user,
            module=task_module,
            title='Implement sorting exercise',
            description='Use quicksort.',
            due_date='2026-10-21',
            priority=Task.Priority.HIGH,
        )
        Task.objects.create(
            user=authenticated_user,
            title='Unrelated task',
            description='Buy notebooks.',
            due_date='2026-10-22',
            priority=Task.Priority.HIGH,
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(
            reverse('task-list'),
            {'search': 'sorting', 'ordering': 'priority'},
        )

        assert response.status_code == status.HTTP_200_OK
        assert [task['title'] for task in response.data] == [
            'Implement sorting exercise',
            'Read sorting notes',
        ]

    def test_filter_tasks_by_next_7_days(self, api_client, authenticated_user):
        today = timezone.localdate()
        upcoming_task = Task.objects.create(
            user=authenticated_user,
            title='Soon task',
            due_date=today + timedelta(days=3),
        )
        Task.objects.create(
            user=authenticated_user,
            title='Later task',
            due_date=today + timedelta(days=14),
        )
        Task.objects.create(
            user=authenticated_user,
            title='Done soon task',
            due_date=today + timedelta(days=2),
            status=Task.Status.DONE,
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(reverse('task-list'), {'due': 'next_7_days'})

        assert response.status_code == status.HTTP_200_OK
        assert {task['id'] for task in response.data} == {
            upcoming_task.id,
            Task.objects.get(title='Done soon task').id,
        }

    def test_filter_overdue_tasks_excludes_done(self, api_client, authenticated_user):
        today = timezone.localdate()
        overdue_task = Task.objects.create(
            user=authenticated_user,
            title='Overdue task',
            due_date=today - timedelta(days=1),
        )
        Task.objects.create(
            user=authenticated_user,
            title='Done overdue task',
            due_date=today - timedelta(days=2),
            status=Task.Status.DONE,
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(reverse('task-list'), {'due': 'overdue'})

        assert response.status_code == status.HTTP_200_OK
        assert [task['id'] for task in response.data] == [overdue_task.id]

    def test_update_task_to_done_sets_completed_at(self, api_client, authenticated_user, study_task):
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.patch(
            reverse('task-detail', args=[study_task.id]),
            {'status': Task.Status.DONE},
            format='json',
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == Task.Status.DONE
        assert response.data['completed_at'] is not None

    def test_cannot_access_other_users_task(self, api_client):
        owner = CustomUser.objects.create_user(
            username='privateowner',
            email='privateowner@example.com',
            password='SecurePass123!',
        )
        visitor = CustomUser.objects.create_user(
            username='privatevisitor',
            email='privatevisitor@example.com',
            password='SecurePass123!',
        )
        task = Task.objects.create(
            user=owner,
            title='Private task',
        )
        api_client.force_authenticate(user=visitor)

        response = api_client.get(reverse('task-detail', args=[task.id]))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_own_task(self, api_client, authenticated_user, study_task):
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.delete(reverse('task-detail', args=[study_task.id]))

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Task.objects.filter(id=study_task.id).exists()
