"""
Tests for progress summary and calendar overview API endpoints.
"""
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import CustomUser
from apps.courses.models import Lecture, StudyModule
from apps.deadlines.models import Deadline
from apps.plans.models import StudyPlanEntry
from apps.tasks.models import Task


@pytest.fixture
def api_client():
    """Fixture providing a DRF API client."""
    return APIClient()


@pytest.mark.django_db
@pytest.mark.integration
class TestProgressSummaryAPI:
    """API tests for the progress summary endpoint."""

    def test_progress_summary_requires_authentication(self, api_client):
        response = api_client.get(reverse('progress-summary'))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_empty_progress_summary(self, api_client, authenticated_user):
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(reverse('progress-summary'))

        assert response.status_code == status.HTTP_200_OK
        assert response.data['modules']['total'] == 0
        assert response.data['tasks']['total'] == 0
        assert response.data['deadlines']['total'] == 0
        assert response.data['study_plans']['total'] == 0
        assert response.data['study_plans']['planned_minutes'] == 0

    def test_progress_summary_counts_only_authenticated_users_data(
        self,
        api_client,
        authenticated_user,
    ):
        today = timezone.localdate()
        module = StudyModule.objects.create(user=authenticated_user, name='Algorithms')
        other_user = CustomUser.objects.create_user(
            username='overviewother',
            email='overviewother@example.com',
            password='SecurePass123!',
        )
        StudyModule.objects.create(user=other_user, name='Other Module')

        Task.objects.create(
            user=authenticated_user,
            module=module,
            title='Overdue task',
            due_date=today - timedelta(days=1),
            status=Task.Status.OPEN,
        )
        Task.objects.create(
            user=authenticated_user,
            module=module,
            title='Done task',
            due_date=today - timedelta(days=1),
            status=Task.Status.DONE,
        )
        Task.objects.create(
            user=authenticated_user,
            module=module,
            title='Active task',
            due_date=today + timedelta(days=3),
            status=Task.Status.IN_PROGRESS,
        )
        Task.objects.create(user=other_user, title='Other task')

        Deadline.objects.create(
            user=authenticated_user,
            module=module,
            title='Upcoming exam',
            deadline_type=Deadline.DeadlineType.EXAM,
            date=today + timedelta(days=10),
        )
        Deadline.objects.create(
            user=authenticated_user,
            module=module,
            title='Overdue assignment',
            date=today - timedelta(days=2),
        )
        Deadline.objects.create(
            user=authenticated_user,
            module=module,
            title='Completed project',
            date=today + timedelta(days=20),
            status=Deadline.Status.COMPLETED,
        )
        Deadline.objects.create(
            user=authenticated_user,
            title='Cancelled presentation',
            date=today + timedelta(days=30),
            status=Deadline.Status.CANCELLED,
        )
        Deadline.objects.create(user=other_user, title='Other deadline', date=today)

        StudyPlanEntry.objects.create(
            user=authenticated_user,
            module=module,
            topic='Planned session',
            planned_date=today + timedelta(days=1),
            duration_minutes=60,
            status=StudyPlanEntry.Status.PLANNED,
        )
        StudyPlanEntry.objects.create(
            user=authenticated_user,
            module=module,
            topic='Active session',
            planned_date=today + timedelta(days=2),
            duration_minutes=90,
            status=StudyPlanEntry.Status.IN_PROGRESS,
        )
        StudyPlanEntry.objects.create(
            user=authenticated_user,
            module=module,
            topic='Done session',
            planned_date=today - timedelta(days=1),
            duration_minutes=120,
            status=StudyPlanEntry.Status.DONE,
        )
        StudyPlanEntry.objects.create(
            user=authenticated_user,
            topic='Skipped session',
            planned_date=today,
            duration_minutes=30,
            status=StudyPlanEntry.Status.SKIPPED,
        )
        StudyPlanEntry.objects.create(
            user=other_user,
            topic='Other session',
            planned_date=today,
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(reverse('progress-summary'))

        assert response.status_code == status.HTTP_200_OK
        assert response.data['modules']['total'] == 1
        assert response.data['tasks'] == {
            'total': 3,
            'open': 1,
            'in_progress': 1,
            'done': 1,
            'overdue': 1,
        }
        assert response.data['deadlines'] == {
            'total': 4,
            'upcoming': 1,
            'overdue': 1,
            'completed': 1,
            'cancelled': 1,
        }
        assert response.data['study_plans'] == {
            'total': 4,
            'planned': 1,
            'in_progress': 1,
            'done': 1,
            'skipped': 1,
            'planned_minutes': 270,
            'completed_minutes': 120,
        }


@pytest.mark.django_db
@pytest.mark.integration
class TestCalendarAPI:
    """API tests for the normalized calendar endpoint."""

    def test_calendar_requires_authentication(self, api_client):
        response = api_client.get(reverse('calendar-events'))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_calendar_returns_owned_normalized_events_sorted(self, api_client, authenticated_user):
        module = StudyModule.objects.create(user=authenticated_user, name='Databases')
        other_user = CustomUser.objects.create_user(
            username='calendarother',
            email='calendarother@example.com',
            password='SecurePass123!',
        )
        Lecture.objects.create(module=module, title='Indexes', date='2026-10-03')
        Task.objects.create(
            user=authenticated_user,
            module=module,
            title='SQL homework',
            due_date='2026-10-02',
            priority=Task.Priority.HIGH,
        )
        Task.objects.create(
            user=authenticated_user,
            module=module,
            title='Task without due date',
        )
        Deadline.objects.create(
            user=authenticated_user,
            module=module,
            title='Database exam',
            deadline_type=Deadline.DeadlineType.EXAM,
            date='2026-10-04',
        )
        StudyPlanEntry.objects.create(
            user=authenticated_user,
            module=module,
            topic='Join practice',
            planned_date='2026-10-01',
            duration_minutes=90,
        )
        Task.objects.create(user=other_user, title='Other task', due_date='2026-10-01')
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(reverse('calendar-events'))

        assert response.status_code == status.HTTP_200_OK
        assert [(event['type'], event['title'], event['date']) for event in response.data] == [
            ('study_plan', 'Join practice', '2026-10-01'),
            ('task', 'SQL homework', '2026-10-02'),
            ('lecture', 'Indexes', '2026-10-03'),
            ('deadline', 'Database exam', '2026-10-04'),
        ]
        assert response.data[1]['priority'] == Task.Priority.HIGH
        assert response.data[2]['module_name'] == module.name
        assert response.data[3]['deadline_type'] == Deadline.DeadlineType.EXAM

    def test_calendar_filters_by_date_range(self, api_client, authenticated_user):
        module = StudyModule.objects.create(user=authenticated_user, name='Math')
        Lecture.objects.create(module=module, title='Too early', date='2026-09-30')
        Lecture.objects.create(module=module, title='In range', date='2026-10-10')
        Lecture.objects.create(module=module, title='Too late', date='2026-11-01')
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(
            reverse('calendar-events'),
            {'date_after': '2026-10-01', 'date_before': '2026-10-31'},
        )

        assert response.status_code == status.HTTP_200_OK
        assert [event['title'] for event in response.data] == ['In range']

    def test_calendar_filters_by_module(self, api_client, authenticated_user):
        selected_module = StudyModule.objects.create(user=authenticated_user, name='Selected')
        other_module = StudyModule.objects.create(user=authenticated_user, name='Other')
        Lecture.objects.create(module=selected_module, title='Selected lecture', date='2026-10-01')
        Lecture.objects.create(module=other_module, title='Other lecture', date='2026-10-01')
        Task.objects.create(
            user=authenticated_user,
            module=selected_module,
            title='Selected task',
            due_date='2026-10-02',
        )
        Task.objects.create(
            user=authenticated_user,
            title='Task without module',
            due_date='2026-10-02',
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(
            reverse('calendar-events'),
            {'module': selected_module.id},
        )

        assert response.status_code == status.HTTP_200_OK
        assert [event['title'] for event in response.data] == [
            'Selected lecture',
            'Selected task',
        ]
        assert all(event['module'] == selected_module.id for event in response.data)
