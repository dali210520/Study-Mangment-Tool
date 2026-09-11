"""
API views for student task management.
"""
from datetime import timedelta

from django.db.models import Case, IntegerField, Q, Value, When
from django.utils import timezone
from rest_framework import generics

from apps.core.query_params import (
    apply_ordering,
    get_choice_param,
    get_date_param,
    get_int_param,
    get_ordering_param,
)

from .models import Task
from .serializers import TaskSerializer


class TaskListCreateView(generics.ListCreateAPIView):
    """List and create tasks for the authenticated user."""

    serializer_class = TaskSerializer
    ordering_fields = {
        'created_at': 'created_at',
        'due_date': 'due_date',
        'status': 'status',
        'title': 'title',
    }

    def get_queryset(self):
        queryset = Task.objects.filter(user=self.request.user).select_related('module')
        query_params = self.request.query_params

        search = query_params.get('search')
        status = get_choice_param(query_params, 'status', Task.Status.values)
        priority = get_choice_param(query_params, 'priority', Task.Priority.values)
        module_id = get_int_param(query_params, 'module')
        due_before = get_date_param(query_params, 'due_before')
        due_after = get_date_param(query_params, 'due_after')
        due = get_choice_param(
            query_params,
            'due',
            {'next_7_days', 'overdue', 'today', 'upcoming'},
        )
        ordering = get_ordering_param(
            query_params,
            [*self.ordering_fields, 'priority'],
        )

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(module__name__icontains=search)
            )
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if module_id:
            queryset = queryset.filter(module_id=module_id)
        if due_before:
            queryset = queryset.filter(due_date__lte=due_before)
        if due_after:
            queryset = queryset.filter(due_date__gte=due_after)
        if due:
            queryset = self._filter_due(queryset, due)

        return self._apply_ordering(queryset, ordering)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def _filter_due(self, queryset, due):
        today = timezone.localdate()

        if due == 'today':
            return queryset.filter(due_date=today)
        if due == 'overdue':
            return queryset.filter(due_date__lt=today).exclude(status=Task.Status.DONE)
        if due == 'upcoming':
            return queryset.filter(due_date__gte=today)
        if due == 'next_7_days':
            return queryset.filter(
                due_date__gte=today,
                due_date__lte=today + timedelta(days=7),
            )
        return queryset

    def _apply_ordering(self, queryset, ordering):
        if not ordering:
            return queryset

        direction = '-' if ordering.startswith('-') else ''
        field = ordering[1:] if direction else ordering

        if field == 'priority':
            queryset = queryset.annotate(
                priority_order=Case(
                    When(priority=Task.Priority.HIGH, then=Value(1)),
                    When(priority=Task.Priority.MEDIUM, then=Value(2)),
                    When(priority=Task.Priority.LOW, then=Value(3)),
                    output_field=IntegerField(),
                )
            )
            return queryset.order_by(f'{direction}priority_order', 'due_date', 'title')

        return apply_ordering(queryset, ordering, self.ordering_fields)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Read, update or delete one task owned by the authenticated user."""

    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).select_related('module')
