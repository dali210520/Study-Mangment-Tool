"""
Tests for user registration backend logic.
"""
import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from apps.accounts.models import CustomUser


@pytest.mark.django_db
@pytest.mark.authentication
class TestUserRegistration:
    """Test cases for user registration backend logic."""

    def test_successful_registration(self, user_data):
        """
        Test: Successful user registration with valid data.
        Scenario: User provides all required fields with valid data.
        Expected: User is created in database.
        """
        user = CustomUser.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', '')
        )
        
        assert user.id is not None
        assert user.username == user_data['username']
        assert user.email == user_data['email']
        assert user.check_password(user_data['password'])

    def test_registration_allows_various_username_lengths(self):
        """
        Test: Various username lengths are allowed.
        Scenario: Users can register with different username lengths.
        Expected: Users are created successfully.
        """
        # Single character username
        user1 = CustomUser.objects.create_user(
            username='a',
            email='user1@example.com',
            password='SecurePass123!'
        )
        assert user1 is not None
        
        # Two character username
        user2 = CustomUser.objects.create_user(
            username='ab',
            email='user2@example.com',
            password='SecurePass123!'
        )
        assert user2 is not None
        
        # Three character username
        user3 = CustomUser.objects.create_user(
            username='abc',
            email='user3@example.com',
            password='SecurePass123!'
        )
        assert user3 is not None

    def test_registration_username_short_allowed_in_create_user(self):
        """
        Test: Short username can be created via create_user().
        Scenario: User creates user with short username directly.
        Expected: User is created (create_user bypasses model validation).
        Note: This is expected Django behavior - validation is optional.
        """
        # create_user doesn't call full_clean() by default
        user = CustomUser.objects.create_user(
            username='ab',
            email='test@example.com',
            password='SecurePass123!'
        )
        
        assert user is not None
        assert user.username == 'ab'

    def test_registration_username_already_exists(self, user_data):
        """
        Test: Registration fails when username is already taken.
        Scenario: User tries to register with an existing username.
        Expected: IntegrityError is raised.
        """
        # Create first user
        CustomUser.objects.create_user(
            username=user_data['username'],
            email='first@example.com',
            password='SecurePass123!'
        )
        
        # Try to create user with same username
        with pytest.raises(IntegrityError):
            CustomUser.objects.create_user(
                username=user_data['username'],
                email='second@example.com',
                password='SecurePass123!'
            )

    def test_registration_email_already_exists(self, user_data):
        """
        Test: Registration fails when email is already registered.
        Scenario: User tries to register with an existing email.
        Expected: IntegrityError is raised.
        """
        # Create first user
        CustomUser.objects.create_user(
            username='firstuser',
            email=user_data['email'],
            password='SecurePass123!'
        )
        
        # Try to create user with same email
        with pytest.raises(IntegrityError):
            CustomUser.objects.create_user(
                username='seconduser',
                email=user_data['email'],
                password='SecurePass123!'
            )

    def test_registration_invalid_email_format(self):
        """
        Test: Registration fails with invalid email format.
        Scenario: User provides email without @ symbol.
        Expected: ValidationError is raised.
        """
        with pytest.raises(ValidationError):
            user = CustomUser(
                username='testuser',
                email='invalid-email-format',
                password='SecurePass123!'
            )
            user.full_clean()

    def test_registration_email_case_insensitive(self, user_data):
        """
        Test: Email handling is case-insensitive.
        Scenario: User registers with UPPERCASE email, then tries lowercase.
        Expected: IntegrityError due to duplicate email (case-insensitive).
        """
        # First registration with normal case
        user1 = CustomUser.objects.create_user(
            username='firstuser',
            email=user_data['email'],
            password='SecurePass123!'
        )
        
        # Email should be stored as lowercase
        assert user1.email == user_data['email'].lower()
        
        # Try to register with same email in different case
        with pytest.raises(IntegrityError):
            CustomUser.objects.create_user(
                username='seconduser',
                email=user_data['email'].upper(),
                password='SecurePass123!'
            )

    def test_registration_user_fields(self, user_data):
        """
        Test: User is created with all provided fields.
        Scenario: User provides first_name and last_name.
        Expected: All fields are stored correctly.
        """
        user = CustomUser.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )
        
        assert user.first_name == user_data['first_name']
        assert user.last_name == user_data['last_name']

    def test_registration_email_is_lowercased(self):
        """
        Test: Email is automatically lowercased during registration.
        Scenario: User provides email with uppercase letters.
        Expected: Email is stored in lowercase.
        """
        user = CustomUser.objects.create_user(
            username='testuser',
            email='TestUser@EXAMPLE.COM',
            password='SecurePass123!'
        )
        
        assert user.email == 'testuser@example.com'

    def test_registration_default_is_email_verified_false(self, user_data):
        """
        Test: New users are not email-verified by default.
        Scenario: User registers.
        Expected: is_email_verified defaults to False.
        """
        user = CustomUser.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password']
        )
        
        assert user.is_email_verified is False

    def test_registration_timestamps_set(self, user_data):
        """
        Test: User timestamps are set automatically.
        Scenario: User is created.
        Expected: created_at and updated_at are set.
        """
        user = CustomUser.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password']
        )
        
        assert user.created_at is not None
        assert user.updated_at is not None
