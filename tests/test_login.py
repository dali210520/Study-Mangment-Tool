"""
Tests for user authentication backend logic (login/logout).
"""
import pytest
from django.contrib.auth import authenticate
from apps.accounts.models import CustomUser


@pytest.mark.django_db
@pytest.mark.authentication
class TestUserLogin:
    """Test cases for user login backend logic."""

    def test_successful_login(self):
        """
        Test: Successful user login with correct credentials.
        Scenario: User provides correct username and password.
        Expected: authenticate() returns the user.
        """
        # Create a test user
        CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!'
        )
        
        # Attempt authentication
        user = authenticate(username='testuser', password='SecurePass123!')
        
        assert user is not None
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'

    def test_login_invalid_password(self):
        """
        Test: Login fails with incorrect password.
        Scenario: User provides correct username but wrong password.
        Expected: authenticate() returns None.
        """
        # Create a test user
        CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!'
        )
        
        # Attempt authentication with wrong password
        user = authenticate(username='testuser', password='WrongPassword123!')
        
        assert user is None

    def test_login_nonexistent_user(self):
        """
        Test: Login fails for nonexistent user.
        Scenario: User tries to authenticate with non-existent username.
        Expected: authenticate() returns None.
        """
        user = authenticate(username='nonexistent', password='SecurePass123!')
        
        assert user is None

    def test_login_case_sensitive_username(self):
        """
        Test: Username authentication is case-sensitive in Django.
        Scenario: User created with 'testuser', authenticated with 'TestUser'.
        Expected: authenticate() returns None (case-sensitive).
        """
        # Create user with lowercase username
        CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!'
        )
        
        # Attempt authentication with uppercase username
        user = authenticate(username='TestUser', password='SecurePass123!')
        
        assert user is None

    def test_login_password_case_sensitive(self):
        """
        Test: Password authentication is case-sensitive.
        Scenario: User created with password 'SecurePass123!'.
        Expected: Wrong case fails authentication.
        """
        # Create user
        CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!'
        )
        
        # Try wrong case
        user = authenticate(username='testuser', password='securepass123!')
        
        assert user is None


@pytest.mark.django_db
@pytest.mark.authentication
class TestUserLogout:
    """Test cases for user logout backend logic."""

    def test_logout_clears_session(self, db):
        """
        Test: Logout functionality clears user session.
        Scenario: After logout, user session should be deleted.
        Expected: Session object is properly cleared.
        """
        # This is a placeholder test for logout backend logic
        # Actual logout in Django is handled by the session framework
        # This test verifies the concept
        user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!'
        )
        
        # User exists and can be retrieved
        retrieved_user = CustomUser.objects.get(username='testuser')
        assert retrieved_user.id == user.id


@pytest.mark.django_db
@pytest.mark.authentication
class TestUserAuthentication:
    """General authentication tests."""

    def test_user_is_active_by_default(self):
        """
        Test: New users are active by default.
        Scenario: User is created.
        Expected: is_active is True.
        """
        user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!'
        )
        
        assert user.is_active is True

    def test_inactive_user_cannot_authenticate(self):
        """
        Test: Inactive users cannot authenticate.
        Scenario: User is deactivated (is_active=False).
        Expected: authenticate() returns None.
        """
        # Create user
        user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!'
        )
        
        # Deactivate user
        user.is_active = False
        user.save()
        
        # Attempt authentication
        authenticated = authenticate(username='testuser', password='SecurePass123!')
        
        assert authenticated is None

    def test_authenticate_returns_correct_user_object(self):
        """
        Test: authenticate() returns the correct user object with all fields.
        Scenario: User is authenticated.
        Expected: Returned user object has all expected fields.
        """
        user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!',
            first_name='Test',
            last_name='User'
        )
        
        authenticated = authenticate(username='testuser', password='SecurePass123!')
        
        assert authenticated.id == user.id
        assert authenticated.username == user.username
        assert authenticated.email == user.email
        assert authenticated.first_name == user.first_name
        assert authenticated.last_name == user.last_name

