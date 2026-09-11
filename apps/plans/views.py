"""
API views for study plans.
"""
from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
from rest_framework import generics

from apps.core.query_params import (
    apply_ordering,
    get_choice_param,
    get_date_param,
    get_int_param,
    get_ordering_param,
)

from .models import StudyPlanEntry
from .serializers import StudyPlanEntrySerializer


class StudyPlanEntryListCreateView(generics.ListCreateAPIView):
    """List and create study plan entries for the authenticated user."""

    serializer_class = StudyPlanEntrySerializer
    ordering_fields = {
        'created_at': 'created_at',
        'duration': 'duration_minutes',
        'planned_date': 'planned_date',
        'status': 'status',
        'topic': 'topic',
    }

    def get_queryset(self):
        queryset = StudyPlanEntry.objects.filter(user=self.request.user).select_related(
            'module',
            'deadline',
        )
        query_params = self.request.query_params

        search = query_params.get('search')
        status = get_choice_param(query_params, 'status', StudyPlanEntry.Status.values)
        module_id = get_int_param(query_params, 'module')
        deadline_id = get_int_param(query_params, 'deadline')
        date_before = get_date_param(query_params, 'date_before')
        date_after = get_date_param(query_params, 'date_after')
        date = get_choice_param(
            query_params,
            'date',
            {'next_7_days', 'past', 'today', 'upcoming'},
        )
        ordering = get_ordering_param(query_params, self.ordering_fields)

        if search:
            queryset = queryset.filter(
                Q(topic__icontains=search)
                | Q(notes__icontains=search)
                | Q(module__name__icontains=search)
                | Q(deadline__title__icontains=search)
            )
        if status:
            queryset = queryset.filter(status=status)
        if module_id:
            queryset = queryset.filter(module_id=module_id)
        if deadline_id:
            queryset = queryset.filter(deadline_id=deadline_id)
        if date_before:
            queryset = queryset.filter(planned_date__lte=date_before)
        if date_after:
            queryset = queryset.filter(planned_date__gte=date_after)
        if date:
            queryset = self._filter_date(queryset, date)

        return apply_ordering(queryset, ordering, self.ordering_fields)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def _filter_date(self, queryset, date):
        today = timezone.localdate()

        if date == 'today':
            return queryset.filter(planned_date=today)
        if date == 'past':
            return queryset.filter(planned_date__lt=today)
        if date == 'upcoming':
            return queryset.filter(planned_date__gte=today)
        if date == 'next_7_days':
            return queryset.filter(
                planned_date__gte=today,
                planned_date__lte=today + timedelta(days=7),
            )
        return queryset

class StudyPlanEntryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Read, update or delete one study plan entry owned by the authenticated user."""

    serializer_class = StudyPlanEntrySerializer

    def get_queryset(self):
        return StudyPlanEntry.objects.filter(user=self.request.user).select_related(
            'module',
            'deadline',
        )
