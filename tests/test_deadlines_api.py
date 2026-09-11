"""
Tests for assignments and exams API endpoints.
"""
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import CustomUser
from apps.courses.models import StudyModule
from apps.deadlines.models import Deadline


@pytest.fixture
def api_client():
    """Fixture providing a DRF API client."""
    return APIClient()


@pytest.fixture
def deadline_module(authenticated_user):
    """Fixture providing a module for deadline tests."""
    return StudyModule.objects.create(
        user=authenticated_user,
        name='Software Engineering',
        semester='WS 2026',
    )


@pytest.fixture
def academic_deadline(authenticated_user, deadline_module):
    """Fixture providing a deadline owned by the authenticated user."""
    return Deadline.objects.create(
        user=authenticated_user,
        module=deadline_module,
        title='Project submission',
        deadline_type=Deadline.DeadlineType.PROJECT,
        date='2026-11-30',
    )


@pytest.mark.django_db
@pytest.mark.integration
class TestDeadlineAPI:
    """API tests for assignments, exams and other deadlines."""

    def test_deadline_list_requires_authentication(self, api_client):
        response = api_client.get(reverse('deadline-list'))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_deadline_for_authenticated_user(
        self,
        api_client,
        authenticated_user,
        deadline_module,
    ):
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.post(
            reverse('deadline-list'),
            {
                'module': deadline_module.id,
                'title': 'Written exam',
                'deadline_type': Deadline.DeadlineType.EXAM,
                'date': '2026-12-12',
                'notes': 'Room A101.',
            },
            format='json',
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Written exam'
        assert response.data['module'] == deadline_module.id
        assert response.data['module_name'] == deadline_module.name
        assert response.data['status'] == Deadline.Status.UPCOMING
        assert Deadline.objects.filter(user=authenticated_user, title='Written exam').exists()

    def test_create_deadline_without_module(self, api_client, authenticated_user):
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.post(
            reverse('deadline-list'),
            {
                'title': 'Scholarship application',
                'deadline_type': Deadline.DeadlineType.OTHER,
                'date': '2026-10-01',
            },
            format='json',
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['module'] is None
        assert response.data['deadline_type'] == Deadline.DeadlineType.OTHER

    def test_create_deadline_rejects_other_users_module(self, api_client, authenticated_user):
        other_user = CustomUser.objects.create_user(
            username='otherdeadlineuser',
            email='otherdeadlineuser@example.com',
            password='SecurePass123!',
        )
        other_module = StudyModule.objects.create(
            user=other_user,
            name='Private Module',
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.post(
            reverse('deadline-list'),
            {
                'module': other_module.id,
                'title': 'Invalid deadline',
                'date': '2026-12-12',
            },
            format='json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not Deadline.objects.filter(title='Invalid deadline').exists()

    def test_list_only_returns_own_deadlines(self, api_client, authenticated_user):
        other_user = CustomUser.objects.create_user(
            username='otherdeadlineowner',
            email='otherdeadlineowner@example.com',
            password='SecurePass123!',
        )
        own_deadline = Deadline.objects.create(
            user=authenticated_user,
            title='Own deadline',
            date='2026-11-20',
        )
        Deadline.objects.create(
            user=other_user,
            title='Other deadline',
            date='2026-11-20',
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(reverse('deadline-list'))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == own_deadline.id

    def test_filter_deadlines_by_type_status_module_and_date(
        self,
        api_client,
        authenticated_user,
        deadline_module,
    ):
        matching_deadline = Deadline.objects.create(
            user=authenticated_user,
            module=deadline_module,
            title='Matching exam',
            deadline_type=Deadline.DeadlineType.EXAM,
            status=Deadline.Status.UPCOMING,
            date='2026-12-10',
        )
        Deadline.objects.create(
            user=authenticated_user,
            module=deadline_module,
            title='Wrong type',
            deadline_type=Deadline.DeadlineType.ASSIGNMENT,
            status=Deadline.Status.UPCOMING,
            date='2026-12-10',
        )
        Deadline.objects.create(
            user=authenticated_user,
            title='Wrong date',
            deadline_type=Deadline.DeadlineType.EXAM,
            status=Deadline.Status.UPCOMING,
            date='2027-01-20',
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(
            reverse('deadline-list'),
            {
                'type': Deadline.DeadlineType.EXAM,
                'status': Deadline.Status.UPCOMING,
                'module': deadline_module.id,
                'date_before': '2026-12-31',
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert [deadline['id'] for deadline in response.data] == [matching_deadline.id]

    def test_search_and_order_deadlines(self, api_client, authenticated_user, deadline_module):
        Deadline.objects.create(
            user=authenticated_user,
            module=deadline_module,
            title='Written exam',
            deadline_type=Deadline.DeadlineType.EXAM,
            date='2026-12-12',
            notes='SQL and normalization.',
        )
        Deadline.objects.create(
            user=authenticated_user,
            module=deadline_module,
            title='SQL project',
            deadline_type=Deadline.DeadlineType.PROJECT,
            date='2026-11-30',
            notes='Build a small schema.',
        )
        Deadline.objects.create(
            user=authenticated_user,
            title='Unrelated deadline',
            date='2026-10-10',
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(
            reverse('deadline-list'),
            {'search': 'sql', 'ordering': '-date'},
        )

        assert response.status_code == status.HTTP_200_OK
        assert [deadline['title'] for deadline in response.data] == [
            'Written exam',
            'SQL project',
        ]

    def test_filter_deadlines_by_next_7_days(self, api_client, authenticated_user):
        today = timezone.localdate()
        upcoming_deadline = Deadline.objects.create(
            user=authenticated_user,
            title='Soon exam',
            date=today + timedelta(days=4),
        )
        Deadline.objects.create(
            user=authenticated_user,
            title='Later exam',
            date=today + timedelta(days=14),
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(reverse('deadline-list'), {'date': 'next_7_days'})

        assert response.status_code == status.HTTP_200_OK
        assert [deadline['id'] for deadline in response.data] == [upcoming_deadline.id]

    def test_filter_overdue_deadlines_only_returns_upcoming_status(
        self,
        api_client,
        authenticated_user,
    ):
        today = timezone.localdate()
        overdue_deadline = Deadline.objects.create(
            user=authenticated_user,
            title='Overdue deadline',
            date=today - timedelta(days=1),
        )
        Deadline.objects.create(
            user=authenticated_user,
            title='Completed overdue deadline',
            date=today - timedelta(days=2),
            status=Deadline.Status.COMPLETED,
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(reverse('deadline-list'), {'date': 'overdue'})

        assert response.status_code == status.HTTP_200_OK
        assert [deadline['id'] for deadline in response.data] == [overdue_deadline.id]

    def test_past_deadline_is_marked_past_due(self, api_client, authenticated_user):
        yesterday = timezone.localdate() - timedelta(days=1)
        deadline = Deadline.objects.create(
            user=authenticated_user,
            title='Past deadline',
            date=yesterday,
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(reverse('deadline-detail', args=[deadline.id]))

        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_past_due'] is True

    def test_update_own_deadline(self, api_client, authenticated_user, academic_deadline):
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.patch(
            reverse('deadline-detail', args=[academic_deadline.id]),
            {'status': Deadline.Status.COMPLETED},
            format='json',
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == Deadline.Status.COMPLETED

    def test_cannot_access_other_users_deadline(self, api_client):
        owner = CustomUser.objects.create_user(
            username='privatedeadlineowner',
            email='privatedeadlineowner@example.com',
            password='SecurePass123!',
        )
        visitor = CustomUser.objects.create_user(
            username='privatedeadlinevisitor',
            email='privatedeadlinevisitor@example.com',
            password='SecurePass123!',
        )
        deadline = Deadline.objects.create(
            user=owner,
            title='Private deadline',
            date='2026-12-12',
        )
        api_client.force_authenticate(user=visitor)

        response = api_client.get(reverse('deadline-detail', args=[deadline.id]))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_own_deadline(self, api_client, authenticated_user, academic_deadline):
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.delete(reverse('deadline-detail', args=[academic_deadline.id]))

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Deadline.objects.filter(id=academic_deadline.id).exists()
