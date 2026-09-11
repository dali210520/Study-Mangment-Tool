"""
API views for registration, login, logout and profile management.
"""
from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    LoginSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
    UserSerializer,
)


class RegisterView(APIView):
    """Create a user account and return the created user data."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Authenticate a user and start a Django session."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request=request,
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
        )
        if user is None:
            return Response(
                {'detail': 'Invalid username or password.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        login(request, user)
        return Response(UserSerializer(user).data)


class LogoutView(APIView):
    """End the current Django session."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserView(APIView):
    """Return information about the authenticated user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ProfileUpdateView(APIView):
    """Update editable profile fields of the authenticated user."""

    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = ProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data)
