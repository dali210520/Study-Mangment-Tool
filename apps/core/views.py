"""
Core API utility endpoints.
"""
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """Lightweight health check for tooling and future UI startup checks."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                'status': 'ok',
                'service': 'study-management-tool',
            }
        )


class ApiInfoView(APIView):
    """Return a compact overview of stable API areas for frontend integration."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                'name': 'Study Management Tool API',
                'status': 'ready',
                'ui': {
                    'login': '/login/',
                    'register': '/register/',
                    'dashboard': '/dashboard/',
                },
                'auth': {
                    'register': '/api/auth/register/',
                    'login': '/api/auth/login/',
                    'logout': '/api/auth/logout/',
                    'current_user': '/api/auth/me/',
                },
                'resources': {
                    'modules': '/api/modules/',
                    'tasks': '/api/tasks/',
                    'deadlines': '/api/deadlines/',
                    'study_plans': '/api/study-plans/',
                    'materials': '/api/materials/',
                    'material_search': '/api/materials/search/',
                    'progress_summary': '/api/progress/summary/',
                    'calendar': '/api/calendar/',
                },
                'query_parameters': {
                    'search': 'Text search on supported list endpoints.',
                    'ordering': 'Sort on supported list endpoints, prefix with - for descending.',
                    'date_filters': 'Use YYYY-MM-DD for date_before, date_after and due/date ranges.',
                    'module': 'Filter related resources by numeric module id.',
                },
            }
        )

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from apps.core.models import Notification

@login_required
@require_POST
def mark_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'ok'})

@login_required
@require_POST
def delete_notification(request, pk):
    Notification.objects.filter(user=request.user, pk=pk).delete()
    return JsonResponse({'status': 'ok'})
