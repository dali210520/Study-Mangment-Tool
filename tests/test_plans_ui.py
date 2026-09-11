"""
Tests for the server-rendered study plan UI.
"""
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import CustomUser
from apps.courses.models import StudyModule
from apps.deadlines.models import Deadline
from apps.plans.models import StudyPlanEntry


@pytest.mark.django_db
@pytest.mark.integration
class TestStudyPlanUI:
    """UI tests for study plan pages."""

    def test_plan_list_requires_login(self, client):
        response = client.get(reverse('ui-plan-list'))

        assert response.status_code == 302
        assert response['Location'].startswith('/login/')

    def test_plan_list_only_shows_owned_entries(self, client, authenticated_user):
        other_user = CustomUser.objects.create_user(
            username='planuiother',
            email='planuiother@example.com',
            password='SecurePass123!',
        )
        StudyPlanEntry.objects.create(
            user=authenticated_user,
            topic='Own study plan',
            planned_date='2027-01-20',
        )
        StudyPlanEntry.objects.create(
            user=other_user,
            topic='Private study plan',
            planned_date='2027-01-20',
        )
        client.force_login(authenticated_user)

        response = client.get(reverse('ui-plan-list'))

        assert response.status_code == 200
        content = response.content.decode()
        assert 'Own study plan' in content
        assert 'Private study plan' not in content

    def test_create_plan_from_ui(self, client, authenticated_user):
        module = StudyModule.objects.create(user=authenticated_user, name='Databases')
        deadline = Deadline.objects.create(
            user=authenticated_user,
            module=module,
            title='Database exam',
            date='2027-01-30',
        )
        client.force_login(authenticated_user)

        response = client.post(
            reverse('ui-plan-create'),
            {
                'module': module.id,
                'deadline': deadline.id,
                'topic': 'Transaction isolation',
                'planned_date': '2027-01-22',
                'duration_minutes': 120,
                'status': StudyPlanEntry.Status.PLANNED,
                'notes': 'Read examples.',
            },
        )

        entry = StudyPlanEntry.objects.get(topic='Transaction isolation')
        assert response.status_code == 302
        assert response['Location'] == reverse('ui-plan-list')
        assert entry.user == authenticated_user
        assert entry.module == module
        assert entry.deadline == deadline

    def test_create_plan_rejects_other_users_links(self, client, authenticated_user):
        other_user = CustomUser.objects.create_user(
            username='planlinkowner',
            email='planlinkowner@example.com',
            password='SecurePass123!',
        )
        other_module = StudyModule.objects.create(user=other_user, name='Private Module')
        other_deadline = Deadline.objects.create(
            user=other_user,
            title='Private exam',
            date='2027-01-30',
        )
        client.force_login(authenticated_user)

        response = client.post(
            reverse('ui-plan-create'),
            {
                'module': other_module.id,
                'deadline': other_deadline.id,
                'topic': 'Invalid plan',
                'planned_date': '2027-01-22',
                'duration_minutes': 60,
                'status': StudyPlanEntry.Status.PLANNED,
            },
        )

        assert response.status_code == 200
        assert not StudyPlanEntry.objects.filter(topic='Invalid plan').exists()

    def test_update_and_delete_plan_from_ui(self, client, authenticated_user):
        module = StudyModule.objects.create(user=authenticated_user, name='Algorithms')
        entry = StudyPlanEntry.objects.create(
            user=authenticated_user,
            module=module,
            topic='Old topic',
            planned_date='2027-01-20',
        )
        client.force_login(authenticated_user)

        update_response = client.post(
            reverse('ui-plan-update', args=[entry.id]),
            {
                'module': module.id,
                'deadline': '',
                'topic': 'Updated topic',
                'planned_date': '2027-01-23',
                'duration_minutes': 90,
                'status': StudyPlanEntry.Status.IN_PROGRESS,
                'notes': 'Updated notes.',
            },
        )

        entry.refresh_from_db()
        assert update_response.status_code == 302
        assert entry.topic == 'Updated topic'
        assert entry.status == StudyPlanEntry.Status.IN_PROGRESS

        delete_response = client.post(reverse('ui-plan-delete', args=[entry.id]))

        assert delete_response.status_code == 302
        assert not StudyPlanEntry.objects.filter(id=entry.id).exists()

    def test_plan_list_filters_search_status_module_deadline_and_date(
        self,
        client,
        authenticated_user,
    ):
        today = timezone.localdate()
        module = StudyModule.objects.create(user=authenticated_user, name='Mathematics')
        deadline = Deadline.objects.create(
            user=authenticated_user,
            module=module,
            title='Analysis exam',
            date=today + timedelta(days=5),
        )
        matching_entry = StudyPlanEntry.objects.create(
            user=authenticated_user,
            module=module,
            deadline=deadline,
            topic='Analysis review',
            planned_date=today + timedelta(days=2),
            status=StudyPlanEntry.Status.IN_PROGRESS,
        )
        StudyPlanEntry.objects.create(
            user=authenticated_user,
            module=module,
            deadline=deadline,
            topic='Analysis planned',
            planned_date=today + timedelta(days=2),
            status=StudyPlanEntry.Status.PLANNED,
        )
        StudyPlanEntry.objects.create(
            user=authenticated_user,
            topic='Analysis unrelated',
            planned_date=today + timedelta(days=14),
            status=StudyPlanEntry.Status.IN_PROGRESS,
        )
        client.force_login(authenticated_user)

        response = client.get(
            reverse('ui-plan-list'),
            {
                'q': 'analysis',
                'status': StudyPlanEntry.Status.IN_PROGRESS,
                'module': module.id,
                'deadline': deadline.id,
                'date': 'next_7_days',
            },
        )

        assert response.status_code == 200
        content = response.content.decode()
        assert matching_entry.topic in content
        assert 'Analysis planned' not in content
        assert 'Analysis unrelated' not in content

    def test_quick_status_update_marks_plan_done(self, client, authenticated_user):
        entry = StudyPlanEntry.objects.create(
            user=authenticated_user,
            topic='Finish reading',
            planned_date='2027-01-20',
        )
        client.force_login(authenticated_user)

        response = client.post(
            reverse('ui-plan-status', args=[entry.id]),
            {'status': StudyPlanEntry.Status.DONE},
        )

        entry.refresh_from_db()
        assert response.status_code == 302
        assert response['Location'] == reverse('ui-plan-list')
        assert entry.status == StudyPlanEntry.Status.DONE

    def test_cannot_access_other_users_plan_ui(self, client, authenticated_user):
        other_user = CustomUser.objects.create_user(
            username='privateuiplanowner',
            email='privateuiplanowner@example.com',
            password='SecurePass123!',
        )
        entry = StudyPlanEntry.objects.create(
            user=other_user,
            topic='Hidden plan',
            planned_date='2027-01-20',
        )
        client.force_login(authenticated_user)

        response = client.get(reverse('ui-plan-update', args=[entry.id]))

        assert response.status_code == 404
