"""
Serializers for account-related API endpoints.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Public representation of the current user."""

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'profile_picture_url',
            'is_email_verified',
        )
        read_only_fields = ('id', 'username', 'email', 'is_email_verified')


class RegisterSerializer(serializers.ModelSerializer):
    """Validate and create a new user account."""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
        )

    def validate_email(self, value):
        """Store emails consistently and reject duplicates early."""
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('A user with that email already exists.')
        return email

    def validate_username(self, value):
        """Return a clear API error when the username is already taken."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('A user with that username already exists.')
        return value

    def validate(self, attrs):
        """Check matching and secure passwords before saving."""
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm', None)

        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })

        validate_password(password)
        return attrs

    def create(self, validated_data):
        """Create the user through Django's user manager."""
        password = validated_data.pop('password')
        return User.objects.create_user(password=password, **validated_data)


class LoginSerializer(serializers.Serializer):
    """Credentials required for login."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Editable profile fields for the authenticated user."""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'bio', 'profile_picture_url')
