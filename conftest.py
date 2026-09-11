"""
Pytest configuration and fixtures.
"""
import os
import django
import pytest
from django.conf import settings
from django.test.utils import get_runner


def pytest_configure():
    """Configure Django settings for pytest."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()


@pytest.fixture
def user_data():
    """Fixture providing valid user registration data."""
    return {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'SecurePass123!',
        'password_confirm': 'SecurePass123!',
        'first_name': 'Test',
        'last_name': 'User'
    }


@pytest.fixture
def invalid_user_data():
    """Fixture providing invalid user registration data."""
    return {
        'username': 'a',  # Too short
        'email': 'invalid-email',  # Invalid format
        'password': 'weak',  # Too weak
        'password_confirm': 'different'  # Doesn't match
    }


@pytest.fixture
def authenticated_user(db):
    """Fixture providing an authenticated user."""
    from apps.accounts.models import CustomUser
    user = CustomUser.objects.create_user(
        username='authuser',
        email='authuser@example.com',
        password='SecurePass123!'
    )
    return user
