"""
Tests for account API endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import CustomUser


@pytest.fixture
def api_client():
    """Fixture providing a DRF API client."""
    return APIClient()


@pytest.mark.django_db
@pytest.mark.authentication
class TestAuthAPI:
    """API tests for registration, login, logout and profile endpoints."""

    def test_register_creates_user(self, api_client, user_data):
        response = api_client.post(reverse('auth-register'), user_data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['username'] == user_data['username']
        assert response.data['email'] == user_data['email']
        assert 'password' not in response.data
        assert CustomUser.objects.filter(username=user_data['username']).exists()

    def test_register_rejects_duplicate_email(self, api_client, user_data):
        CustomUser.objects.create_user(
            username='existing',
            email=user_data['email'],
            password='SecurePass123!',
        )

        response = api_client.post(reverse('auth-register'), user_data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    def test_login_returns_current_user_data(self, api_client):
        CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!',
        )

        response = api_client.post(
            reverse('auth-login'),
            {'username': 'testuser', 'password': 'SecurePass123!'},
            format='json',
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'testuser'

    def test_login_rejects_invalid_credentials(self, api_client):
        response = api_client.post(
            reverse('auth-login'),
            {'username': 'missing', 'password': 'wrong'},
            format='json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['detail'] == 'Invalid username or password.'

    def test_me_requires_authentication(self, api_client):
        response = api_client.get(reverse('auth-me'))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_me_returns_authenticated_user(self, api_client, authenticated_user):
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(reverse('auth-me'))

        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == authenticated_user.username

    def test_profile_update_changes_editable_fields(self, api_client, authenticated_user):
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.put(
            reverse('auth-profile-update'),
            {
                'first_name': 'Updated',
                'last_name': 'Student',
                'bio': 'Learning Django step by step.',
            },
            format='json',
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'
        assert response.data['last_name'] == 'Student'
        assert response.data['bio'] == 'Learning Django step by step.'

    def test_logout_requires_authentication(self, api_client):
        response = api_client.post(reverse('auth-logout'))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_logout_authenticated_user(self, api_client, authenticated_user):
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.post(reverse('auth-logout'))

        assert response.status_code == status.HTTP_204_NO_CONTENT
