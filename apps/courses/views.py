"""
API views for study modules and lectures.
"""
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics

from apps.core.query_params import apply_ordering, get_date_param, get_ordering_param

from .models import Lecture, StudyModule
from .serializers import LectureSerializer, StudyModuleSerializer


class StudyModuleListCreateView(generics.ListCreateAPIView):
    """List and create modules for the authenticated user."""

    serializer_class = StudyModuleSerializer
    ordering_fields = {
        'name': 'name',
        'semester': 'semester',
        'lecturer': 'lecturer',
        'created_at': 'created_at',
    }

    def get_queryset(self):
        queryset = StudyModule.objects.filter(user=self.request.user)
        query_params = self.request.query_params

        search = query_params.get('search')
        ordering = get_ordering_param(query_params, self.ordering_fields)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(semester__icontains=search)
                | Q(lecturer__icontains=search)
                | Q(description__icontains=search)
            )

        return apply_ordering(queryset, ordering, self.ordering_fields)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StudyModuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Read, update or delete one module owned by the authenticated user."""

    serializer_class = StudyModuleSerializer

    def get_queryset(self):
        return StudyModule.objects.filter(user=self.request.user)


class LectureListCreateView(generics.ListCreateAPIView):
    """List and create lectures for one owned module."""

    serializer_class = LectureSerializer
    ordering_fields = {
        'date': 'date',
        'title': 'title',
        'created_at': 'created_at',
    }

    def get_module(self):
        return get_object_or_404(
            StudyModule,
            id=self.kwargs['module_id'],
            user=self.request.user,
        )

    def get_queryset(self):
        queryset = Lecture.objects.filter(module=self.get_module())
        query_params = self.request.query_params

        search = query_params.get('search')
        date_before = get_date_param(query_params, 'date_before')
        date_after = get_date_param(query_params, 'date_after')
        ordering = get_ordering_param(query_params, self.ordering_fields)

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(notes__icontains=search)
            )
        if date_before:
            queryset = queryset.filter(date__lte=date_before)
        if date_after:
            queryset = queryset.filter(date__gte=date_after)

        return apply_ordering(queryset, ordering, self.ordering_fields)

    def perform_create(self, serializer):
        serializer.save(module=self.get_module())


class LectureDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Read, update or delete one lecture from an owned module."""

    serializer_class = LectureSerializer

    def get_queryset(self):
        return Lecture.objects.filter(module__user=self.request.user)
