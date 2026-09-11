"""
URL routes for task management API endpoints.
"""
from django.urls import path

from .views import TaskDetailView, TaskListCreateView


urlpatterns = [
    path('tasks/', TaskListCreateView.as_view(), name='task-list'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
]
