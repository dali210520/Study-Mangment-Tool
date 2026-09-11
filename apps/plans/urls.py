"""
URL routes for study plan API endpoints.
"""
from django.urls import path

from .views import StudyPlanEntryDetailView, StudyPlanEntryListCreateView


urlpatterns = [
    path('study-plans/', StudyPlanEntryListCreateView.as_view(), name='study-plan-list'),
    path('study-plans/<int:pk>/', StudyPlanEntryDetailView.as_view(), name='study-plan-detail'),
]
