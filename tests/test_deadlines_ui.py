"""
Tests for the server-rendered assignments and exams UI.
"""
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import CustomUser
from apps.courses.models import StudyModule
from apps.deadlines.models import Deadline


@pytest.mark.django_db
@pytest.mark.integration
class TestDeadlineUI:
    """UI tests for assignment and exam pages."""

    def test_deadline_list_requires_login(self, client):
        response = client.get(reverse('ui-deadline-list'))

        assert response.status_code == 302
        assert response['Location'].startswith('/login/')

    def test_deadline_list_only_shows_owned_deadlines(self, client, authenticated_user):
        other_user = CustomUser.objects.create_user(
            username='deadlineuiother',
            email='deadlineuiother@example.com',
            password='SecurePass123!',
        )
        Deadline.objects.create(
            user=authenticated_user,
            title='Own exam',
            date='2027-01-20',
        )
        Deadline.objects.create(
            user=other_user,
            title='Private exam',
            date='2027-01-20',
        )
        client.force_login(authenticated_user)

        response = client.get(reverse('ui-deadline-list'))

        assert response.status_code == 200
        content = response.content.decode()
        assert 'Own exam' in content
        assert 'Private exam' not in content

    def test_create_deadline_from_ui(self, client, authenticated_user):
        module = StudyModule.objects.create(user=authenticated_user, name='Software Engineering')
        client.force_login(authenticated_user)

        response = client.post(
            reverse('ui-deadline-create'),
            {
                'module': module.id,
                'title': 'Requirements presentation',
                'deadline_type': Deadline.DeadlineType.PRESENTATION,
                'date': '2027-01-22',
                'notes': 'Slides and demo.',
                'status': Deadline.Status.UPCOMING,
            },
        )

        deadline = Deadline.objects.get(title='Requirements presentation')
        assert response.status_code == 302
        assert response['Location'] == reverse('ui-deadline-list')
        assert deadline.user == authenticated_user
        assert deadline.module == module

    def test_create_deadline_rejects_other_users_module(self, client, authenticated_user):
        other_user = CustomUser.objects.create_user(
            username='deadlinemoduleowner',
            email='deadlinemoduleowner@example.com',
            password='SecurePass123!',
        )
        other_module = StudyModule.objects.create(user=other_user, name='Private Module')
        client.force_login(authenticated_user)

        response = client.post(
            reverse('ui-deadline-create'),
            {
                'module': other_module.id,
                'title': 'Invalid exam',
                'deadline_type': Deadline.DeadlineType.EXAM,
                'date': '2027-01-22',
                'status': Deadline.Status.UPCOMING,
            },
        )

        assert response.status_code == 200
        assert not Deadline.objects.filter(title='Invalid exam').exists()

    def test_update_and_delete_deadline_from_ui(self, client, authenticated_user):
        module = StudyModule.objects.create(user=authenticated_user, name='Databases')
        deadline = Deadline.objects.create(
            user=authenticated_user,
            module=module,
            title='Old exam',
            date='2027-01-20',
        )
        client.force_login(authenticated_user)

        update_response = client.post(
            reverse('ui-deadline-update', args=[deadline.id]),
            {
                'module': module.id,
                'title': 'Updated exam',
                'deadline_type': Deadline.DeadlineType.EXAM,
                'date': '2027-01-23',
                'notes': 'Room B201.',
                'status': Deadline.Status.COMPLETED,
            },
        )

        deadline.refresh_from_db()
        assert update_response.status_code == 302
        assert deadline.title == 'Updated exam'
        assert deadline.status == Deadline.Status.COMPLETED

        delete_response = client.post(reverse('ui-deadline-delete', args=[deadline.id]))

        assert delete_response.status_code == 302
        assert not Deadline.objects.filter(id=deadline.id).exists()

    def test_deadline_list_filters_search_type_status_module_and_date(
        self,
        client,
        authenticated_user,
    ):
        today = timezone.localdate()
        module = StudyModule.objects.create(user=authenticated_user, name='Mathematics')
        matching_deadline = Deadline.objects.create(
            user=authenticated_user,
            module=module,
            title='Analysis exam',
            deadline_type=Deadline.DeadlineType.EXAM,
            status=Deadline.Status.UPCOMING,
            date=today - timedelta(days=1),
        )
        Deadline.objects.create(
            user=authenticated_user,
            module=module,
            title='Analysis assignment',
            deadline_type=Deadline.DeadlineType.ASSIGNMENT,
            status=Deadline.Status.UPCOMING,
            date=today - timedelta(days=1),
        )
        Deadline.objects.create(
            user=authenticated_user,
            title='Analysis completed exam',
            deadline_type=Deadline.DeadlineType.EXAM,
            status=Deadline.Status.COMPLETED,
            date=today - timedelta(days=1),
        )
        client.force_login(authenticated_user)

        response = client.get(
            reverse('ui-deadline-list'),
            {
                'q': 'analysis',
                'type': Deadline.DeadlineType.EXAM,
                'status': Deadline.Status.UPCOMING,
                'module': module.id,
                'date': 'overdue',
            },
        )

        assert response.status_code == 200
        content = response.content.decode()
        assert matching_deadline.title in content
        assert 'Analysis assignment' not in content
        assert 'Analysis completed exam' not in content

    def test_quick_status_update_marks_deadline_completed(self, client, authenticated_user):
        deadline = Deadline.objects.create(
            user=authenticated_user,
            title='Finish project',
            date='2027-01-20',
        )
        client.force_login(authenticated_user)

        response = client.post(
            reverse('ui-deadline-status', args=[deadline.id]),
            {'status': Deadline.Status.COMPLETED},
        )

        deadline.refresh_from_db()
        assert response.status_code == 302
        assert response['Location'] == reverse('ui-deadline-list')
        assert deadline.status == Deadline.Status.COMPLETED

    def test_cannot_access_other_users_deadline_ui(self, client, authenticated_user):
        other_user = CustomUser.objects.create_user(
            username='privateuideadlineowner',
            email='privateuideadlineowner@example.com',
            password='SecurePass123!',
        )
        deadline = Deadline.objects.create(
            user=other_user,
            title='Hidden exam',
            date='2027-01-20',
        )
        client.force_login(authenticated_user)

        response = client.get(reverse('ui-deadline-update', args=[deadline.id]))

        assert response.status_code == 404
