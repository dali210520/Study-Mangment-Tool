"""
URL routes for assignments and exams API endpoints.
"""
from django.urls import path

from .views import DeadlineDetailView, DeadlineListCreateView


urlpatterns = [
    path('deadlines/', DeadlineListCreateView.as_view(), name='deadline-list'),
    path('deadlines/<int:pk>/', DeadlineDetailView.as_view(), name='deadline-detail'),
]
