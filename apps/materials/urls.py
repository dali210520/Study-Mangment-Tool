"""
URL routes for study material API endpoints.
"""
from django.urls import path

from .views import (
    StudyMaterialDetailView,
    StudyMaterialListCreateView,
    StudyMaterialSearchView,
)


urlpatterns = [
    path('materials/', StudyMaterialListCreateView.as_view(), name='material-list'),
    path('materials/search/', StudyMaterialSearchView.as_view(), name='material-search'),
    path('materials/<int:pk>/', StudyMaterialDetailView.as_view(), name='material-detail'),
]
