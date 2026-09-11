"""
Tests for shared query parameter validation.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.courses.models import StudyModule


@pytest.fixture
def api_client():
    """Fixture providing a DRF API client."""
    return APIClient()


@pytest.mark.django_db
@pytest.mark.integration
class TestQueryParamValidation:
    """API tests for invalid filter and ordering parameters."""

    def test_module_list_rejects_unknown_ordering(self, api_client, authenticated_user):
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(reverse('module-list'), {'ordering': 'unknown'})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'ordering' in response.data

    def test_lecture_list_rejects_invalid_date(self, api_client, authenticated_user):
        module = StudyModule.objects.create(user=authenticated_user, name='Math')
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(
            reverse('lecture-list', args=[module.id]),
            {'date_before': 'tomorrow'},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'date_before' in response.data

    def test_task_list_rejects_invalid_choice(self, api_client, authenticated_user):
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(reverse('task-list'), {'status': 'almost_done'})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'status' in response.data

    def test_task_list_rejects_invalid_module_id(self, api_client, authenticated_user):
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(reverse('task-list'), {'module': 'abc'})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'module' in response.data

    def test_calendar_rejects_invalid_date(self, api_client, authenticated_user):
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(reverse('calendar-events'), {'date_after': 'next-week'})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'date_after' in response.data

    def test_material_search_rejects_invalid_module_id(self, api_client, authenticated_user):
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(
            reverse('material-search'),
            {'q': 'sql', 'module': 'not-a-number'},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'module' in response.data
