"""
Server-rendered views for progress and overview pages.
"""
from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView

from apps.overview.services import build_calendar_events, build_progress_summary


EVENT_LABELS = {
    'lecture': 'Vorlesung',
    'task': 'Aufgabe',
    'deadline': 'Termin',
    'study_plan': 'Lernplan',
}


class ProgressView(LoginRequiredMixin, TemplateView):
    """Show a readable progress overview for the authenticated user."""

    template_name = 'ui/progress/progress.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        summary = build_progress_summary(self.request.user)
        today = timezone.localdate()
        events = build_calendar_events(
            self.request.user,
            date_after=today,
            date_before=today + timedelta(days=14),
        )[:8]

        context.update(
            {
                'active_nav': 'progress',
                'summary': summary,
                'task_done_percent': self._percent(
                    summary['tasks']['done'],
                    summary['tasks']['total'],
                ),
                'study_done_percent': self._percent(
                    summary['study_plans']['completed_minutes'],
                    summary['study_plans']['planned_minutes'],
                ),
                'deadline_done_percent': self._percent(
                    summary['deadlines']['completed'],
                    summary['deadlines']['total'],
                ),
                'upcoming_events': [
                    {
                        **event,
                        'label': EVENT_LABELS.get(event['type'], event['type']),
                    }
                    for event in events
                ],
            }
        )
        return context

    def _percent(self, value, total):
        if not total:
            return 0
        return round((value / total) * 100)
