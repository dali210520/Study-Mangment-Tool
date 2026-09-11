"""
Tests for the server-rendered dashboard UI.
"""
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import CustomUser
from apps.courses.models import Lecture, StudyModule
from apps.deadlines.models import Deadline
from apps.plans.models import StudyPlanEntry
from apps.tasks.models import Task


@pytest.mark.django_db
@pytest.mark.integration
class TestDashboardUI:
    """UI tests for the authenticated dashboard."""

    def test_home_redirects_to_dashboard(self, client):
        response = client.get(reverse('home'))

        assert response.status_code == 302
        assert response['Location'] == reverse('dashboard')

    def test_dashboard_requires_login(self, client):
        response = client.get(reverse('dashboard'))

        assert response.status_code == 302
        assert response['Location'].startswith('/login/')

    def test_dashboard_renders_summary_and_upcoming_events(self, client, authenticated_user):
        today = timezone.localdate()
        module = StudyModule.objects.create(user=authenticated_user, name='Databases')
        other_user = CustomUser.objects.create_user(
            username='dashboardother',
            email='dashboardother@example.com',
            password='SecurePass123!',
        )

        Lecture.objects.create(
            module=module,
            title='Index lecture',
            date=today + timedelta(days=2),
        )
        Task.objects.create(
            user=authenticated_user,
            module=module,
            title='SQL homework',
            due_date=today + timedelta(days=1),
            status=Task.Status.OPEN,
        )
        Task.objects.create(
            user=authenticated_user,
            title='Finished reading',
            status=Task.Status.DONE,
        )
        Deadline.objects.create(
            user=authenticated_user,
            module=module,
            title='Database exam',
            deadline_type=Deadline.DeadlineType.EXAM,
            date=today + timedelta(days=5),
        )
        StudyPlanEntry.objects.create(
            user=authenticated_user,
            module=module,
            topic='Join practice',
            planned_date=today + timedelta(days=3),
            duration_minutes=60,
            status=StudyPlanEntry.Status.DONE,
        )
        Task.objects.create(
            user=other_user,
            title='Other private task',
            due_date=today + timedelta(days=1),
        )

        client.force_login(authenticated_user)
        response = client.get(reverse('dashboard'))

        assert response.status_code == 200
        content = response.content.decode()
        assert 'Dashboard' in content
        assert 'Databases' in content
        assert 'SQL homework' in content
        assert 'Database exam' in content
        assert 'Join practice' in content
        assert 'Other private task' not in content
        assert '50%' in content
        assert '100%' in content

    def test_dashboard_shows_empty_event_state(self, client, authenticated_user):
        client.force_login(authenticated_user)

        response = client.get(reverse('dashboard'))

        assert response.status_code == 200
        assert 'Keine Termine in den nächsten 14 Tagen.' in response.content.decode()
