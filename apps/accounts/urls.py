"""
URL routes for account-related API endpoints.
"""
from django.urls import path

from .views import (
    CurrentUserView,
    LoginView,
    LogoutView,
    ProfileUpdateView,
    RegisterView,
)


urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('me/', CurrentUserView.as_view(), name='auth-me'),
    path('profile/update/', ProfileUpdateView.as_view(), name='auth-profile-update'),
]
