"""
Tests for the server-rendered authentication UI.
"""
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()


@pytest.mark.django_db
@pytest.mark.integration
class TestAuthUI:
    """UI tests for login, registration and logout."""

    def test_login_page_is_public(self, client):
        response = client.get(reverse('login'))

        assert response.status_code == 200
        assert 'Anmelden' in response.content.decode()
        assert 'Account erstellen' in response.content.decode()

    def test_register_page_is_public(self, client):
        response = client.get(reverse('register'))

        assert response.status_code == 200
        assert 'Registrieren' in response.content.decode()

    def test_register_creates_user_and_logs_in(self, client):
        response = client.post(
            reverse('register'),
            {
                'username': 'newstudent',
                'email': 'newstudent@example.com',
                'first_name': 'New',
                'last_name': 'Student',
                'password': 'SecurePass123!',
                'password_confirm': 'SecurePass123!',
            },
        )

        assert response.status_code == 302
        assert response['Location'] == reverse('dashboard')
        assert User.objects.filter(username='newstudent').exists()

        dashboard_response = client.get(reverse('dashboard'))
        assert dashboard_response.status_code == 200

    def test_login_authenticates_existing_user(self, client):
        User.objects.create_user(
            username='student',
            email='student@example.com',
            password='SecurePass123!',
        )

        response = client.post(
            reverse('login'),
            {
                'username': 'student',
                'password': 'SecurePass123!',
            },
        )

        assert response.status_code == 302
        assert response['Location'] == reverse('dashboard')

    def test_logout_ends_session(self, client, authenticated_user):
        client.force_login(authenticated_user)

        response = client.post(reverse('logout'))

        assert response.status_code == 302
        assert response['Location'] == reverse('login')

        dashboard_response = client.get(reverse('dashboard'))
        assert dashboard_response.status_code == 302
