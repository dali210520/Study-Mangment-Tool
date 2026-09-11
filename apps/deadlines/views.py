"""
API views for assignments, exams and other deadlines.
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

from .models import Deadline
from .serializers import DeadlineSerializer


class DeadlineListCreateView(generics.ListCreateAPIView):
    """List and create deadlines for the authenticated user."""

    serializer_class = DeadlineSerializer
    ordering_fields = {
        'date': 'date',
        'status': 'status',
        'title': 'title',
        'type': 'deadline_type',
        'created_at': 'created_at',
    }

    def get_queryset(self):
        queryset = Deadline.objects.filter(user=self.request.user).select_related('module')
        query_params = self.request.query_params

        search = query_params.get('search')
        deadline_type = get_choice_param(
            query_params,
            'type',
            Deadline.DeadlineType.values,
        )
        status = get_choice_param(query_params, 'status', Deadline.Status.values)
        module_id = get_int_param(query_params, 'module')
        date_before = get_date_param(query_params, 'date_before')
        date_after = get_date_param(query_params, 'date_after')
        date = get_choice_param(
            query_params,
            'date',
            {'next_7_days', 'overdue', 'today', 'upcoming'},
        )
        ordering = get_ordering_param(query_params, self.ordering_fields)

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(notes__icontains=search)
                | Q(module__name__icontains=search)
            )
        if deadline_type:
            queryset = queryset.filter(deadline_type=deadline_type)
        if status:
            queryset = queryset.filter(status=status)
        if module_id:
            queryset = queryset.filter(module_id=module_id)
        if date_before:
            queryset = queryset.filter(date__lte=date_before)
        if date_after:
            queryset = queryset.filter(date__gte=date_after)
        if date:
            queryset = self._filter_date(queryset, date)

        return apply_ordering(queryset, ordering, self.ordering_fields)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def _filter_date(self, queryset, date):
        today = timezone.localdate()

        if date == 'today':
            return queryset.filter(date=today)
        if date == 'overdue':
            return queryset.filter(
                date__lt=today,
                status=Deadline.Status.UPCOMING,
            )
        if date == 'upcoming':
            return queryset.filter(date__gte=today)
        if date == 'next_7_days':
            return queryset.filter(
                date__gte=today,
                date__lte=today + timedelta(days=7),
            )
        return queryset

class DeadlineDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Read, update or delete one deadline owned by the authenticated user."""

    serializer_class = DeadlineSerializer

    def get_queryset(self):
        return Deadline.objects.filter(user=self.request.user).select_related('module')
