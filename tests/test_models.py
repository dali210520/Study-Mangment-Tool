"""
Tests for CustomUser model.
"""
import pytest
from django.core.exceptions import ValidationError
from apps.accounts.models import CustomUser


@pytest.mark.django_db
@pytest.mark.unit
class TestCustomUserModel:
    """Test cases for CustomUser model."""

    def test_create_user_successful(self):
        """
        Test: Creating a user with valid data.
        Scenario: All required fields are provided.
        Expected: User is created successfully.
        """
        user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!'
        )
        
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.check_password('SecurePass123!')

    def test_user_email_unique(self):
        """
        Test: Email field is unique.
        Scenario: Two users with same email.
        Expected: Second user creation raises error.
        """
        CustomUser.objects.create_user(
            username='user1',
            email='test@example.com',
            password='SecurePass123!'
        )
        
        with pytest.raises(Exception):  # IntegrityError
            CustomUser.objects.create_user(
                username='user2',
                email='test@example.com',
                password='SecurePass123!'
            )

    def test_user_email_lowercase(self):
        """
        Test: Email is converted to lowercase.
        Scenario: User provides email with uppercase letters.
        Expected: Email is stored in lowercase.
        """
        user = CustomUser.objects.create_user(
            username='testuser',
            email='Test@Example.COM',
            password='SecurePass123!'
        )
        
        assert user.email == 'test@example.com'

    def test_user_str_representation(self):
        """
        Test: User string representation.
        Scenario: User object is converted to string.
        Expected: Returns 'username (email)' format.
        """
        user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!'
        )
        
        assert str(user) == 'testuser (test@example.com)'

    def test_user_invalid_email_format(self):
        """
        Test: Invalid email format is rejected.
        Scenario: User email without @ symbol.
        Expected: ValidationError is raised.
        """
        user = CustomUser(
            username='testuser',
            email='invalid-email',
            password='SecurePass123!'
        )
        
        with pytest.raises(ValidationError):
            user.full_clean()

    def test_user_timestamps(self):
        """
        Test: User creation and update timestamps.
        Scenario: User is created and timestamps are recorded.
        Expected: created_at and updated_at are set.
        """
        user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!'
        )
        
        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.created_at <= user.updated_at

    def test_user_default_email_verification(self):
        """
        Test: New user is not email verified by default.
        Scenario: User is created.
        Expected: is_email_verified is False.
        """
        user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!'
        )
        
        assert user.is_email_verified is False
