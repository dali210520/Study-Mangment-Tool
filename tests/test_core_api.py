"""
Tests for core API utility endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """Fixture providing a DRF API client."""
    return APIClient()


@pytest.mark.django_db
@pytest.mark.integration
class TestCoreAPI:
    """API tests for health and metadata endpoints."""

    def test_health_check_is_public(self, api_client):
        response = api_client.get(reverse('api-health'))

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'status': 'ok',
            'service': 'study-management-tool',
        }

    def test_api_root_is_public_and_lists_resources(self, api_client):
        response = api_client.get(reverse('api-root'))

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'ready'
        assert response.data['auth']['login'] == '/api/auth/login/'
        assert response.data['resources']['modules'] == '/api/modules/'
        assert response.data['resources']['calendar'] == '/api/calendar/'

