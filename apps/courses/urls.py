"""
URL routes for module and lecture API endpoints.
"""
from django.urls import path

from .views import (
    LectureDetailView,
    LectureListCreateView,
    StudyModuleDetailView,
    StudyModuleListCreateView,
)


urlpatterns = [
    path('modules/', StudyModuleListCreateView.as_view(), name='module-list'),
    path('modules/<int:pk>/', StudyModuleDetailView.as_view(), name='module-detail'),
    path(
        'modules/<int:module_id>/lectures/',
        LectureListCreateView.as_view(),
        name='lecture-list',
    ),
    path('lectures/<int:pk>/', LectureDetailView.as_view(), name='lecture-detail'),
]
