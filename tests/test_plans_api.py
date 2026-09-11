"""
Tests for study plan API endpoints.
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
from apps.plans.models import StudyPlanEntry


@pytest.fixture
def api_client():
    """Fixture providing a DRF API client."""
    return APIClient()


@pytest.fixture
def plan_module(authenticated_user):
    """Fixture providing a module for study plan tests."""
    return StudyModule.objects.create(
        user=authenticated_user,
        name='Databases',
        semester='WS 2026',
    )


@pytest.fixture
def plan_deadline(authenticated_user, plan_module):
    """Fixture providing a deadline for study plan tests."""
    return Deadline.objects.create(
        user=authenticated_user,
        module=plan_module,
        title='Database exam',
        deadline_type=Deadline.DeadlineType.EXAM,
        date='2026-12-15',
    )


@pytest.fixture
def study_plan_entry(authenticated_user, plan_module, plan_deadline):
    """Fixture providing a study plan entry owned by the authenticated user."""
    return StudyPlanEntry.objects.create(
        user=authenticated_user,
        module=plan_module,
        deadline=plan_deadline,
        topic='SQL joins',
        planned_date='2026-11-20',
        duration_minutes=90,
    )


@pytest.mark.django_db
@pytest.mark.integration
class TestStudyPlanAPI:
    """API tests for study plan entries."""

    def test_study_plan_list_requires_authentication(self, api_client):
        response = api_client.get(reverse('study-plan-list'))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_study_plan_entry_with_module_and_deadline(
        self,
        api_client,
        authenticated_user,
        plan_module,
        plan_deadline,
    ):
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.post(
            reverse('study-plan-list'),
            {
                'module': plan_module.id,
                'deadline': plan_deadline.id,
                'topic': 'Transaction isolation',
                'planned_date': '2026-11-21',
                'duration_minutes': 120,
                'notes': 'Focus on examples.',
            },
            format='json',
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['topic'] == 'Transaction isolation'
        assert response.data['module'] == plan_module.id
        assert response.data['module_name'] == plan_module.name
        assert response.data['deadline'] == plan_deadline.id
        assert response.data['deadline_title'] == plan_deadline.title
        assert response.data['status'] == StudyPlanEntry.Status.PLANNED
        assert StudyPlanEntry.objects.filter(
            user=authenticated_user,
            topic='Transaction isolation',
        ).exists()

    def test_create_study_plan_entry_without_links(self, api_client, authenticated_user):
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.post(
            reverse('study-plan-list'),
            {
                'topic': 'General review',
                'planned_date': '2026-11-22',
            },
            format='json',
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['module'] is None
        assert response.data['deadline'] is None
        assert response.data['duration_minutes'] == 60

    def test_create_study_plan_entry_rejects_zero_duration(self, api_client, authenticated_user):
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.post(
            reverse('study-plan-list'),
            {
                'topic': 'Broken plan',
                'planned_date': '2026-11-22',
                'duration_minutes': 0,
            },
            format='json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'duration_minutes' in response.data

    def test_create_study_plan_rejects_other_users_module(self, api_client, authenticated_user):
        other_user = CustomUser.objects.create_user(
            username='otherplanmodule',
            email='otherplanmodule@example.com',
            password='SecurePass123!',
        )
        other_module = StudyModule.objects.create(user=other_user, name='Private Module')
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.post(
            reverse('study-plan-list'),
            {
                'module': other_module.id,
                'topic': 'Invalid plan',
                'planned_date': '2026-11-22',
            },
            format='json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not StudyPlanEntry.objects.filter(topic='Invalid plan').exists()

    def test_create_study_plan_rejects_other_users_deadline(self, api_client, authenticated_user):
        other_user = CustomUser.objects.create_user(
            username='otherplandeadline',
            email='otherplandeadline@example.com',
            password='SecurePass123!',
        )
        other_deadline = Deadline.objects.create(
            user=other_user,
            title='Private deadline',
            date='2026-12-12',
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.post(
            reverse('study-plan-list'),
            {
                'deadline': other_deadline.id,
                'topic': 'Invalid deadline plan',
                'planned_date': '2026-11-22',
            },
            format='json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not StudyPlanEntry.objects.filter(topic='Invalid deadline plan').exists()

    def test_list_only_returns_own_study_plan_entries(self, api_client, authenticated_user):
        other_user = CustomUser.objects.create_user(
            username='otherplanowner',
            email='otherplanowner@example.com',
            password='SecurePass123!',
        )
        own_entry = StudyPlanEntry.objects.create(
            user=authenticated_user,
            topic='Own plan',
            planned_date='2026-11-20',
        )
        StudyPlanEntry.objects.create(
            user=other_user,
            topic='Other plan',
            planned_date='2026-11-20',
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(reverse('study-plan-list'))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == own_entry.id

    def test_filter_study_plan_entries_by_status_module_deadline_and_date(
        self,
        api_client,
        authenticated_user,
        plan_module,
        plan_deadline,
    ):
        matching_entry = StudyPlanEntry.objects.create(
            user=authenticated_user,
            module=plan_module,
            deadline=plan_deadline,
            topic='Matching plan',
            planned_date='2026-11-20',
            status=StudyPlanEntry.Status.IN_PROGRESS,
        )
        StudyPlanEntry.objects.create(
            user=authenticated_user,
            module=plan_module,
            deadline=plan_deadline,
            topic='Wrong status',
            planned_date='2026-11-20',
            status=StudyPlanEntry.Status.PLANNED,
        )
        StudyPlanEntry.objects.create(
            user=authenticated_user,
            topic='Wrong date',
            planned_date='2027-01-10',
            status=StudyPlanEntry.Status.IN_PROGRESS,
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(
            reverse('study-plan-list'),
            {
                'status': StudyPlanEntry.Status.IN_PROGRESS,
                'module': plan_module.id,
                'deadline': plan_deadline.id,
                'date_before': '2026-12-01',
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert [entry['id'] for entry in response.data] == [matching_entry.id]

    def test_search_and_order_study_plan_entries(
        self,
        api_client,
        authenticated_user,
        plan_module,
        plan_deadline,
    ):
        StudyPlanEntry.objects.create(
            user=authenticated_user,
            module=plan_module,
            deadline=plan_deadline,
            topic='SQL practice',
            planned_date='2026-11-20',
            duration_minutes=60,
        )
        StudyPlanEntry.objects.create(
            user=authenticated_user,
            module=plan_module,
            deadline=plan_deadline,
            topic='SQL exam review',
            planned_date='2026-11-21',
            duration_minutes=120,
        )
        StudyPlanEntry.objects.create(
            user=authenticated_user,
            topic='Unrelated plan',
            planned_date='2026-11-22',
            duration_minutes=180,
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(
            reverse('study-plan-list'),
            {'search': 'sql', 'ordering': '-duration'},
        )

        assert response.status_code == status.HTTP_200_OK
        assert [entry['topic'] for entry in response.data] == [
            'SQL exam review',
            'SQL practice',
        ]

    def test_filter_study_plan_entries_by_next_7_days(self, api_client, authenticated_user):
        today = timezone.localdate()
        upcoming_entry = StudyPlanEntry.objects.create(
            user=authenticated_user,
            topic='Soon study session',
            planned_date=today + timedelta(days=4),
        )
        StudyPlanEntry.objects.create(
            user=authenticated_user,
            topic='Later study session',
            planned_date=today + timedelta(days=14),
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(reverse('study-plan-list'), {'date': 'next_7_days'})

        assert response.status_code == status.HTTP_200_OK
        assert [entry['id'] for entry in response.data] == [upcoming_entry.id]

    def test_filter_study_plan_entries_by_past_date(self, api_client, authenticated_user):
        today = timezone.localdate()
        past_entry = StudyPlanEntry.objects.create(
            user=authenticated_user,
            topic='Past study session',
            planned_date=today - timedelta(days=1),
        )
        StudyPlanEntry.objects.create(
            user=authenticated_user,
            topic='Future study session',
            planned_date=today + timedelta(days=1),
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(reverse('study-plan-list'), {'date': 'past'})

        assert response.status_code == status.HTTP_200_OK
        assert [entry['id'] for entry in response.data] == [past_entry.id]

    def test_update_own_study_plan_entry(self, api_client, authenticated_user, study_plan_entry):
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.patch(
            reverse('study-plan-detail', args=[study_plan_entry.id]),
            {'status': StudyPlanEntry.Status.DONE},
            format='json',
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == StudyPlanEntry.Status.DONE

    def test_cannot_access_other_users_study_plan_entry(self, api_client):
        owner = CustomUser.objects.create_user(
            username='privateplanowner',
            email='privateplanowner@example.com',
            password='SecurePass123!',
        )
        visitor = CustomUser.objects.create_user(
            username='privateplanvisitor',
            email='privateplanvisitor@example.com',
            password='SecurePass123!',
        )
        entry = StudyPlanEntry.objects.create(
            user=owner,
            topic='Private plan',
            planned_date='2026-11-20',
        )
        api_client.force_authenticate(user=visitor)

        response = api_client.get(reverse('study-plan-detail', args=[entry.id]))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_own_study_plan_entry(self, api_client, authenticated_user, study_plan_entry):
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.delete(reverse('study-plan-detail', args=[study_plan_entry.id]))

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not StudyPlanEntry.objects.filter(id=study_plan_entry.id).exists()
