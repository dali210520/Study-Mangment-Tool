"""
URL routes for overview and analytics API endpoints.
"""
from django.urls import path

from .views import CalendarEventListView, ProgressSummaryView


urlpatterns = [
    path('progress/summary/', ProgressSummaryView.as_view(), name='progress-summary'),
    path('calendar/', CalendarEventListView.as_view(), name='calendar-events'),
]
