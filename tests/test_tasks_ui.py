"""
Tests for the server-rendered task UI.
"""
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import CustomUser
from apps.courses.models import StudyModule
from apps.tasks.models import Task


@pytest.mark.django_db
@pytest.mark.integration
class TestTaskUI:
    """UI tests for task pages."""

    def test_task_list_requires_login(self, client):
        response = client.get(reverse('ui-task-list'))

        assert response.status_code == 302
        assert response['Location'].startswith('/login/')

    def test_task_list_only_shows_owned_tasks(self, client, authenticated_user):
        other_user = CustomUser.objects.create_user(
            username='taskuiother',
            email='taskuiother@example.com',
            password='SecurePass123!',
        )
        Task.objects.create(user=authenticated_user, title='Own task')
        Task.objects.create(user=other_user, title='Private task')
        client.force_login(authenticated_user)

        response = client.get(reverse('ui-task-list'))

        assert response.status_code == 200
        content = response.content.decode()
        assert 'Own task' in content
        assert 'Private task' not in content

    def test_create_task_from_ui(self, client, authenticated_user):
        module = StudyModule.objects.create(user=authenticated_user, name='Databases')
        client.force_login(authenticated_user)

        response = client.post(
            reverse('ui-task-create'),
            {
                'module': module.id,
                'title': 'Prepare SQL exercise',
                'description': 'Joins and indexes.',
                'due_date': '2027-01-20',
                'priority': Task.Priority.HIGH,
                'status': Task.Status.OPEN,
            },
        )

        task = Task.objects.get(title='Prepare SQL exercise')
        assert response.status_code == 302
        assert response['Location'] == reverse('ui-task-list')
        assert task.user == authenticated_user
        assert task.module == module

    def test_create_task_rejects_other_users_module(self, client, authenticated_user):
        other_user = CustomUser.objects.create_user(
            username='taskmoduleowner',
            email='taskmoduleowner@example.com',
            password='SecurePass123!',
        )
        other_module = StudyModule.objects.create(user=other_user, name='Private Module')
        client.force_login(authenticated_user)

        response = client.post(
            reverse('ui-task-create'),
            {
                'module': other_module.id,
                'title': 'Invalid task',
                'due_date': '2027-01-20',
                'priority': Task.Priority.MEDIUM,
                'status': Task.Status.OPEN,
            },
        )

        assert response.status_code == 200
        assert not Task.objects.filter(title='Invalid task').exists()

    def test_update_and_delete_task_from_ui(self, client, authenticated_user):
        module = StudyModule.objects.create(user=authenticated_user, name='Math')
        task = Task.objects.create(user=authenticated_user, module=module, title='Old task')
        client.force_login(authenticated_user)

        update_response = client.post(
            reverse('ui-task-update', args=[task.id]),
            {
                'module': module.id,
                'title': 'Updated task',
                'description': 'Updated description.',
                'due_date': '2027-01-21',
                'priority': Task.Priority.LOW,
                'status': Task.Status.IN_PROGRESS,
            },
        )

        task.refresh_from_db()
        assert update_response.status_code == 302
        assert task.title == 'Updated task'
        assert task.status == Task.Status.IN_PROGRESS

        delete_response = client.post(reverse('ui-task-delete', args=[task.id]))

        assert delete_response.status_code == 302
        assert not Task.objects.filter(id=task.id).exists()

    def test_task_list_filters_search_status_priority_module_and_due(self, client, authenticated_user):
        today = timezone.localdate()
        module = StudyModule.objects.create(user=authenticated_user, name='Algorithms')
        matching_task = Task.objects.create(
            user=authenticated_user,
            module=module,
            title='Sorting worksheet',
            due_date=today - timedelta(days=1),
            priority=Task.Priority.HIGH,
            status=Task.Status.IN_PROGRESS,
        )
        Task.objects.create(
            user=authenticated_user,
            module=module,
            title='Sorting done',
            due_date=today - timedelta(days=2),
            priority=Task.Priority.HIGH,
            status=Task.Status.DONE,
        )
        Task.objects.create(
            user=authenticated_user,
            title='Unrelated worksheet',
            due_date=today - timedelta(days=1),
            priority=Task.Priority.HIGH,
            status=Task.Status.IN_PROGRESS,
        )
        client.force_login(authenticated_user)

        response = client.get(
            reverse('ui-task-list'),
            {
                'q': 'sorting',
                'status': Task.Status.IN_PROGRESS,
                'priority': Task.Priority.HIGH,
                'module': module.id,
                'due': 'overdue',
            },
        )

        assert response.status_code == 200
        content = response.content.decode()
        assert matching_task.title in content
        assert 'Sorting done' not in content
        assert 'Unrelated worksheet' not in content

    def test_quick_status_update_sets_completed_at(self, client, authenticated_user):
        task = Task.objects.create(user=authenticated_user, title='Finish notes')
        client.force_login(authenticated_user)

        response = client.post(
            reverse('ui-task-status', args=[task.id]),
            {'status': Task.Status.DONE},
        )

        task.refresh_from_db()
        assert response.status_code == 302
        assert response['Location'] == reverse('ui-task-list')
        assert task.status == Task.Status.DONE
        assert task.completed_at is not None

    def test_cannot_access_other_users_task_ui(self, client, authenticated_user):
        other_user = CustomUser.objects.create_user(
            username='privateuitaskowner',
            email='privateuitaskowner@example.com',
            password='SecurePass123!',
        )
        task = Task.objects.create(user=other_user, title='Hidden task')
        client.force_login(authenticated_user)

        response = client.get(reverse('ui-task-update', args=[task.id]))

        assert response.status_code == 404
