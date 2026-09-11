import json
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.courses.models import Lecture
from apps.tasks.models import Task
from apps.deadlines.models import Deadline
from apps.plans.models import StudyPlanEntry

def apply_new_time(obj, new_time_str):
    if not new_time_str:
        return
    try:
        new_st = datetime.strptime(new_time_str, '%H:%M').time()
        if hasattr(obj, 'start_time') and hasattr(obj, 'end_time') and obj.start_time and obj.end_time:
            # Calculate duration
            st_dt = datetime.combine(datetime.today(), obj.start_time)
            et_dt = datetime.combine(datetime.today(), obj.end_time)
            if et_dt < st_dt:
                et_dt += timedelta(days=1)
            duration = et_dt - st_dt
            
            obj.start_time = new_st
            new_et_dt = datetime.combine(datetime.today(), new_st) + duration
            obj.end_time = new_et_dt.time()
        elif hasattr(obj, 'start_time'):
            obj.start_time = new_st
    except Exception:
        pass

class CalendarEventMoveAPIView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            event_type = data.get('event_type')
            event_id = data.get('event_id')
            new_date = data.get('new_date')
            new_time = data.get('new_time')

            if not all([event_type, event_id, new_date]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            model_map = {
                'lecture': Lecture,
                'task': Task,
                'deadline': Deadline,
                'study_plan': StudyPlanEntry
            }
            
            ModelClass = model_map.get(event_type)
            if not ModelClass:
                return JsonResponse({'error': 'Invalid event type'}, status=400)

            obj = ModelClass.objects.filter(id=event_id, user=request.user).first()
            if not obj:
                return JsonResponse({'error': 'Event not found'}, status=404)

            if event_type == 'lecture':
                obj.date = new_date
            elif event_type == 'task':
                obj.due_date = new_date
            elif event_type == 'deadline':
                obj.date = new_date
            elif event_type == 'study_plan':
                obj.planned_date = new_date

            apply_new_time(obj, new_time)
            obj.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class CalendarEventCopyAPIView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            event_type = data.get('event_type')
            event_id = data.get('event_id')
            new_date = data.get('new_date')
            new_time = data.get('new_time')

            if not all([event_type, event_id, new_date]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            model_map = {
                'lecture': Lecture,
                'task': Task,
                'deadline': Deadline,
                'study_plan': StudyPlanEntry
            }
            
            ModelClass = model_map.get(event_type)
            if not ModelClass:
                return JsonResponse({'error': 'Invalid event type'}, status=400)

            obj = ModelClass.objects.filter(id=event_id, user=request.user).first()
            if not obj:
                return JsonResponse({'error': 'Event not found'}, status=404)

            obj.pk = None
            obj.id = None
            
            if event_type == 'lecture':
                obj.date = new_date
            elif event_type == 'task':
                obj.due_date = new_date
            elif event_type == 'deadline':
                obj.date = new_date
            elif event_type == 'study_plan':
                obj.planned_date = new_date

            apply_new_time(obj, new_time)
            obj.save()
            return JsonResponse({'status': 'success', 'new_id': obj.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
