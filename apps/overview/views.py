"""
API views for progress summaries and calendar events.
"""
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.query_params import get_date_param, get_int_param
from apps.overview.services import build_calendar_events, build_progress_summary


class ProgressSummaryView(APIView):
    """Return a compact progress summary for the authenticated user."""

    def get(self, request):
        return Response(build_progress_summary(request.user))


class CalendarEventListView(APIView):
    """Return normalized calendar events from lectures, tasks, deadlines and plans."""

    def get(self, request):
        date_after = get_date_param(request.query_params, 'date_after')
        date_before = get_date_param(request.query_params, 'date_before')
        module_id = get_int_param(request.query_params, 'module')

        return Response(
            build_calendar_events(
                request.user,
                date_after=date_after,
                date_before=date_before,
                module_id=module_id,
            )
        )
