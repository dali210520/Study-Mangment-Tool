"""
Shared overview calculations for API and dashboard views.
"""
from django.db.models import Sum
from django.utils import timezone

from apps.courses.models import Lecture, StudyModule
from apps.deadlines.models import Deadline
from apps.plans.models import StudyPlanEntry
from apps.tasks.models import Task


def build_progress_summary(user):
    """Return progress counters for one user."""
    today = timezone.localdate()

    tasks = Task.objects.filter(user=user)
    deadlines = Deadline.objects.filter(user=user)
    study_plan_entries = StudyPlanEntry.objects.filter(user=user)

    planned_minutes = study_plan_entries.exclude(
        status=StudyPlanEntry.Status.SKIPPED,
    ).aggregate(total=Sum('duration_minutes'))['total'] or 0
    completed_minutes = study_plan_entries.filter(
        status=StudyPlanEntry.Status.DONE,
    ).aggregate(total=Sum('duration_minutes'))['total'] or 0

    return {
        'modules': {
            'total': StudyModule.objects.filter(user=user).count(),
        },
        'tasks': {
            'total': tasks.count(),
            'open': tasks.filter(status=Task.Status.OPEN).count(),
            'in_progress': tasks.filter(status=Task.Status.IN_PROGRESS).count(),
            'done': tasks.filter(status=Task.Status.DONE).count(),
            'overdue': tasks.filter(
                due_date__lt=today,
            ).exclude(status=Task.Status.DONE).count(),
        },
        'deadlines': {
            'total': deadlines.count(),
            'upcoming': deadlines.filter(
                date__gte=today,
                status=Deadline.Status.UPCOMING,
            ).count(),
            'overdue': deadlines.filter(
                date__lt=today,
                status=Deadline.Status.UPCOMING,
            ).count(),
            'completed': deadlines.filter(status=Deadline.Status.COMPLETED).count(),
            'cancelled': deadlines.filter(status=Deadline.Status.CANCELLED).count(),
        },
        'study_plans': {
            'total': study_plan_entries.count(),
            'planned': study_plan_entries.filter(
                status=StudyPlanEntry.Status.PLANNED,
            ).count(),
            'in_progress': study_plan_entries.filter(
                status=StudyPlanEntry.Status.IN_PROGRESS,
            ).count(),
            'done': study_plan_entries.filter(
                status=StudyPlanEntry.Status.DONE,
            ).count(),
            'skipped': study_plan_entries.filter(
                status=StudyPlanEntry.Status.SKIPPED,
            ).count(),
            'planned_minutes': planned_minutes,
            'completed_minutes': completed_minutes,
        },
    }


def build_calendar_events(user, date_after=None, date_before=None, module_id=None):
    """Return normalized calendar events from lectures, tasks, deadlines and plans."""
    events = []
    events.extend(_lecture_events(user, date_after, date_before, module_id))
    events.extend(_task_events(user, date_after, date_before, module_id))
    events.extend(_deadline_events(user, date_after, date_before, module_id))
    events.extend(_study_plan_events(user, date_after, date_before, module_id))

    return sorted(events, key=lambda event: (event['date'], event['type'], event['title']))


def _lecture_events(user, date_after, date_before, module_id):
    queryset = Lecture.objects.filter(module__user=user).select_related('module')
    queryset = _filter_by_date(queryset, 'date', date_after, date_before)
    if module_id:
        queryset = queryset.filter(module_id=module_id)

    return [
        {
            'id': lecture.id,
            'type': 'lecture',
            'title': lecture.title,
            'date': lecture.date.isoformat(),
            'start_time': lecture.start_time.isoformat() if lecture.start_time else None,
            'end_time': lecture.end_time.isoformat() if lecture.end_time else None,
            'module': lecture.module_id,
            'module_name': lecture.module.name,
            'status': None,
        }
        for lecture in queryset
    ]


def _task_events(user, date_after, date_before, module_id):
    queryset = Task.objects.filter(
        user=user,
        due_date__isnull=False,
    ).select_related('module')
    queryset = _filter_by_date(queryset, 'due_date', date_after, date_before)
    if module_id:
        queryset = queryset.filter(module_id=module_id)

    return [
        {
            'id': task.id,
            'type': 'task',
            'title': task.title,
            'date': task.due_date.isoformat(),
            'start_time': task.start_time.isoformat() if task.start_time else None,
            'end_time': task.end_time.isoformat() if task.end_time else None,
            'module': task.module_id,
            'module_name': task.module.name if task.module else None,
            'status': task.status,
            'priority': task.priority,
        }
        for task in queryset
    ]


def _deadline_events(user, date_after, date_before, module_id):
    queryset = Deadline.objects.filter(user=user).select_related('module')
    queryset = _filter_by_date(queryset, 'date', date_after, date_before)
    if module_id:
        queryset = queryset.filter(module_id=module_id)

    return [
        {
            'id': deadline.id,
            'type': 'deadline',
            'title': deadline.title,
            'date': deadline.date.isoformat(),
            'start_time': deadline.start_time.isoformat() if deadline.start_time else None,
            'end_time': deadline.end_time.isoformat() if deadline.end_time else None,
            'module': deadline.module_id,
            'module_name': deadline.module.name if deadline.module else None,
            'status': deadline.status,
            'deadline_type': deadline.deadline_type,
        }
        for deadline in queryset
    ]


def _study_plan_events(user, date_after, date_before, module_id):
    queryset = StudyPlanEntry.objects.filter(user=user).select_related('module')
    queryset = _filter_by_date(queryset, 'planned_date', date_after, date_before)
    if module_id:
        queryset = queryset.filter(module_id=module_id)

    return [
        {
            'id': entry.id,
            'type': 'study_plan',
            'title': entry.topic,
            'date': entry.planned_date.isoformat(),
            'module': entry.module_id,
            'module_name': entry.module.name if entry.module else None,
            'status': entry.status,
            'duration_minutes': entry.duration_minutes,
        }
        for entry in queryset
    ]


def _filter_by_date(queryset, field_name, date_after, date_before):
    if date_after:
        queryset = queryset.filter(**{f'{field_name}__gte': date_after})
    if date_before:
        queryset = queryset.filter(**{f'{field_name}__lte': date_before})
    return queryset
