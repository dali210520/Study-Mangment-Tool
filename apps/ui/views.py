"""
Server-rendered views for the student dashboard.
"""
import calendar
from datetime import date, timedelta

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import FormView
from django.views.generic import TemplateView

from apps.courses.models import StudyModule
from apps.materials.models import StudyMaterial
from apps.overview.services import build_calendar_events, build_progress_summary
from apps.plans.models import StudyPlanEntry
from apps.tasks.models import Task

from .forms import RegistrationForm


class UserLoginView(LoginView):
    """Login page for regular users."""

    template_name = 'ui/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or reverse('dashboard')


class UserRegisterView(FormView):
    """Registration page for regular users."""

    template_name = 'ui/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


class UserLogoutView(LogoutView):
    """Logout regular users and return them to the login page."""

    next_page = reverse_lazy('login')


class DashboardView(LoginRequiredMixin, TemplateView):
    """Render the authenticated user's dashboard overview."""

    template_name = 'ui/dashboard.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        summary = build_progress_summary(self.request.user)
        upcoming_events = build_calendar_events(
            self.request.user,
            date_after=today,
            date_before=today + timedelta(days=14),
        )
        week_events = build_calendar_events(
            self.request.user,
            date_after=week_start,
            date_before=week_end,
        )

        week_plan_entries = StudyPlanEntry.objects.filter(
            user=self.request.user,
            planned_date__gte=week_start,
            planned_date__lte=week_end,
        )
        week_planned_minutes = (
            sum(entry.duration_minutes for entry in week_plan_entries if entry.status != StudyPlanEntry.Status.SKIPPED)
        )
        week_completed_minutes = sum(
            entry.duration_minutes
            for entry in week_plan_entries
            if entry.status == StudyPlanEntry.Status.DONE
        )

        context.update(
            {
                'summary': summary,
                'active_nav': 'dashboard',
                'metrics': self._build_metrics(summary, today, week_completed_minutes, week_planned_minutes),
                'events': upcoming_events[:5],
                'today': today,
                'window_end': today + timedelta(days=14),
                'week_start': week_start,
                'week_end': week_end,
                'week_days': self._build_week_days(week_start, today),
                'schedule_hours': ['08:00', '10:00', '12:00', '14:00', '16:00'],
                'schedule_events': self._build_schedule_events(week_events, week_start),
                'module_cards': self._build_module_cards(),
                'recent_materials': self._build_recent_materials(),
                'task_status_rows': self._build_task_status_rows(summary),
                'task_status_conic': self._build_task_status_conic(summary),
                'task_total': summary['tasks']['total'],
                'task_completion_percent': self._percent(
                    summary['tasks']['done'],
                    summary['tasks']['total'],
                ),
                'study_completion_percent': self._percent(
                    week_completed_minutes,
                    week_planned_minutes,
                ),
            }
        )
        return context

    def _percent(self, current, total):
        if not total:
            return 0
        return min(round((current / total) * 100), 100)

    def _build_metrics(self, summary, today, week_completed_minutes, week_planned_minutes):
        next_week = today + timedelta(days=7)
        due_soon_tasks = Task.objects.filter(
            user=self.request.user,
            due_date__gte=today,
            due_date__lte=next_week,
        ).exclude(status=Task.Status.DONE).count()

        return {
            'modules': {
                'value': summary['modules']['total'],
                'note': 'aktive Module',
            },
            'open_tasks': {
                'value': summary['tasks']['open'],
                'note': f'{due_soon_tasks} fällig in 7 Tagen',
            },
            'overdue': {
                'value': summary['tasks']['overdue'] + summary['deadlines']['overdue'],
                'note': 'Aufgaben und Termine',
            },
            'study_time': {
                'value': self._format_minutes(week_completed_minutes),
                'note': f'von {self._format_minutes(week_planned_minutes)} Ziel',
            },
        }

    def _build_week_days(self, week_start, today):
        labels = ['MO', 'DI', 'MI', 'DO', 'FR', 'SA', 'SO']
        return [
            {
                'label': labels[index],
                'number': (week_start + timedelta(days=index)).day,
                'is_today': week_start + timedelta(days=index) == today,
            }
            for index in range(7)
        ]

    def _build_schedule_events(self, events, week_start):
        schedule_events = []
        for index, event in enumerate(events[:8]):
            event_date = date.fromisoformat(event['date'])
            day_index = (event_date - week_start).days + 1
            if day_index < 1 or day_index > 7:
                continue
            schedule_events.append(
                {
                    **event,
                    'day_index': day_index,
                    'slot_index': (index % 5) + 1,
                    'time': self._event_time(event),
                }
            )
        return schedule_events

    def _build_module_cards(self):
        modules = StudyModule.objects.filter(user=self.request.user).prefetch_related(
            'tasks',
            'study_plan_entries',
        )[:4]
        return [
            {
                'name': module.name,
                'id': module.id,
                'lecturer': module.lecturer or module.semester or 'Ohne Zusatzinfo',
                'progress': self._module_progress(module),
            }
            for module in modules
        ]

    def _module_progress(self, module):
        task_total = module.tasks.count()
        task_done = module.tasks.filter(status=Task.Status.DONE).count()
        plan_total = module.study_plan_entries.exclude(
            status=StudyPlanEntry.Status.SKIPPED,
        ).count()
        plan_done = module.study_plan_entries.filter(status=StudyPlanEntry.Status.DONE).count()
        return self._percent(task_done + plan_done, task_total + plan_total)

    def _build_recent_materials(self):
        materials = StudyMaterial.objects.filter(
            user=self.request.user,
        ).select_related('module').order_by('-created_at')[:3]
        return [
            {
                'title': material.original_filename or material.title,
                'module_name': material.module.name,
                'created_at': material.created_at,
                'size': self._format_file_size(material),
            }
            for material in materials
        ]

    def _build_task_status_rows(self, summary):
        total = summary['tasks']['total']
        rows = [
            ('Erledigt', summary['tasks']['done'], 'done'),
            ('In Bearbeitung', summary['tasks']['in_progress'], 'progress'),
            ('Offen', summary['tasks']['open'], 'open'),
            ('Überfällig', summary['tasks']['overdue'], 'overdue'),
        ]
        return [
            {
                'label': label,
                'value': value,
                'percent': self._percent(value, total),
                'key': key,
            }
            for label, value, key in rows
        ]

    def _build_task_status_conic(self, summary):
        total = summary['tasks']['total']
        if not total:
            return '#e7edf6 0deg 360deg'

        done = self._degrees(summary['tasks']['done'], total)
        progress = self._degrees(summary['tasks']['in_progress'], total)
        open_tasks = self._degrees(summary['tasks']['open'], total)
        return (
            f'#52b957 0deg {done}deg, '
            f'#2f63f4 {done}deg {done + progress}deg, '
            f'#f1a13a {done + progress}deg {done + progress + open_tasks}deg, '
            f'#e34e4e {done + progress + open_tasks}deg 360deg'
        )

    def _degrees(self, value, total):
        return round((value / total) * 360)

    def _event_time(self, event):
        if event['type'] == 'task':
            return '23:59'
        if event['type'] == 'deadline':
            return '10:00'
        if event['type'] == 'lecture':
            return '08:30'
        return '--'

    def _format_minutes(self, minutes):
        hours = minutes // 60
        remaining_minutes = minutes % 60
        return f'{hours}:{remaining_minutes:02d} h'

    def _format_file_size(self, material):
        try:
            size = material.file.size
        except (OSError, ValueError):
            return f'{material.page_count} Seiten'

        if size < 1024 * 1024:
            return f'{round(size / 1024, 1)} KB'
        return f'{round(size / (1024 * 1024), 1)} MB'


class CalendarView(LoginRequiredMixin, TemplateView):
    """Render the full calendar grid."""

    template_name = 'ui/calendar.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        today = timezone.localdate()
        year = int(self.request.GET.get('year', today.year))
        month = int(self.request.GET.get('month', today.month))
        
        _, num_days = calendar.monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, num_days)
        
        events = build_calendar_events(
            self.request.user,
            date_after=start_date,
            date_before=end_date,
        )
        
        from collections import defaultdict
        events_by_day = defaultdict(list)
        for event in events:
            day = int(event['date'].split('-')[2])
            events_by_day[day].append(event)
            
        cal = calendar.Calendar(firstweekday=0)
        month_days = cal.monthdayscalendar(year, month)
        
        calendar_grid = []
        for week in month_days:
            week_data = []
            for day in week:
                if day == 0:
                    week_data.append({'day': None, 'events': [], 'is_today': False})
                else:
                    is_today = (day == today.day and month == today.month and year == today.year)
                    week_data.append({
                        'day': day,
                        'events': events_by_day[day],
                        'is_today': is_today
                    })
            calendar_grid.append(week_data)
            
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1
        
        months_de = ['', 'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
            
        context.update({
            'active_nav': 'dashboard',
            'year': year,
            'month': month,
            'month_name': f"{months_de[month]} {year}",
            'calendar_grid': calendar_grid,
            'prev_month': f'?year={prev_year}&month={prev_month}',
            'next_month': f'?year={next_year}&month={next_month}',
            'week_days': ['MO', 'DI', 'MI', 'DO', 'FR', 'SA', 'SO'],
            'today': today,
        })
        return context



class CalendarDayView(LoginRequiredMixin, TemplateView):
    template_name = 'ui/calendar_day.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        
        target_date = date(year, month, day)
        
        events = build_calendar_events(
            self.request.user,
            date_after=target_date,
            date_before=target_date,
        )
        
        months_de = ['', 'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
        date_formatted = f"{day}. {months_de[month]} {year}"
        
        time_blocks = [
            {'num': 1, 'start': '08:00', 'end': '08:45'},
            {'num': 2, 'start': '09:00', 'end': '09:45'},
            {'num': 3, 'start': '10:00', 'end': '10:45'},
            {'num': 4, 'start': '11:00', 'end': '11:45'},
            {'num': 5, 'start': '12:00', 'end': '12:45'},
            {'num': 6, 'start': '13:00', 'end': '13:45'},
            {'num': 7, 'start': '14:00', 'end': '14:45'},
            {'num': 8, 'start': '15:00', 'end': '15:45'},
            {'num': 9, 'start': '16:00', 'end': '16:45'},
            {'num': 10, 'start': '17:00', 'end': '17:45'},
            {'num': 11, 'start': '18:00', 'end': '18:45'},
            {'num': 12, 'start': '19:00', 'end': '19:45'},
        ]
        
        grid = {b['num']: [] for b in time_blocks}
        all_day_events = []
        
        for ev in events:
            start_t = ev.get('start_time')
            end_t = ev.get('end_time')
            
            if start_t:
                for b in time_blocks:
                    b_start = b['start'] + ':00'
                    b_end = b['end'] + ':00'
                    if (start_t <= b_start and end_t >= b_end) or (start_t == b_start):
                        grid[b['num']].append(ev)
            else:
                all_day_events.append(ev)

        # Navigation
        prev_day = target_date - timedelta(days=1)
        next_day = target_date + timedelta(days=1)

        context.update({
            'active_nav': 'dashboard',
            'target_date': target_date,
            'date_formatted': date_formatted,
            'events': events,
            'date_str': target_date.isoformat(),
            'time_blocks': time_blocks,
            'grid': grid,
            'all_day_events': all_day_events,
            'prev_day_url': reverse('ui-calendar-day', args=[prev_day.year, prev_day.month, prev_day.day]),
            'next_day_url': reverse('ui-calendar-day', args=[next_day.year, next_day.month, next_day.day]),
        })
        return context

from django.contrib import messages
from apps.core.services import import_davinci_schedule

class DaVinciImportView(LoginRequiredMixin, TemplateView):
    template_name = 'ui/import_davinci.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_nav'] = 'lectures'
        return context

    def post(self, request, *args, **kwargs):
        url = request.POST.get('davinci_url')
        if url:
            try:
                count = import_davinci_schedule(url, request.user)
                messages.success(request, f'Erfolgreich {count} Termine aus daVinci importiert!')
                return redirect('ui-calendar')
            except Exception as e:
                messages.error(request, f'Fehler beim Importieren: {str(e)}')
        else:
            messages.error(request, 'Bitte gib einen gültigen Link ein.')
            
        return self.render_to_response(self.get_context_data())


class CalendarWeekView(LoginRequiredMixin, TemplateView):
    template_name = 'ui/calendar_week.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        
        target_date = date(year, month, day)
        week_start = target_date - timedelta(days=target_date.weekday())
        week_end = week_start + timedelta(days=6)
        
        events = build_calendar_events(
            self.request.user,
            date_after=week_start,
            date_before=week_end,
        )
        
        # Navigation
        prev_week = week_start - timedelta(days=7)
        next_week = week_start + timedelta(days=7)
        
        months_de = ['', 'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
        week_title = f"{week_start.day}. {months_de[week_start.month]} - {week_end.day}. {months_de[week_end.month]} {week_end.year}"
        
        days_of_week = []
        for i in range(7):
            d = week_start + timedelta(days=i)
            days_of_week.append({
                'date': d,
                'name': ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'][i],
                'is_today': d == timezone.localdate(),
                'col_idx': i
            })
            
        time_blocks = [
            {'num': 1, 'start': '08:00', 'end': '08:45'},
            {'num': 2, 'start': '09:00', 'end': '09:45'},
            {'num': 3, 'start': '10:00', 'end': '10:45'},
            {'num': 4, 'start': '11:00', 'end': '11:45'},
            {'num': 5, 'start': '12:00', 'end': '12:45'},
            {'num': 6, 'start': '13:00', 'end': '13:45'},
            {'num': 7, 'start': '14:00', 'end': '14:45'},
            {'num': 8, 'start': '15:00', 'end': '15:45'},
            {'num': 9, 'start': '16:00', 'end': '16:45'},
            {'num': 10, 'start': '17:00', 'end': '17:45'},
            {'num': 11, 'start': '18:00', 'end': '18:45'},
            {'num': 12, 'start': '19:00', 'end': '19:45'},
        ]
        
        # Build grid: block_idx -> day_idx -> list of events
        # Initialize grid
        grid = {b['num']: {d: [] for d in range(7)} for b in time_blocks}
        all_day_events = {d: [] for d in range(7)}
        
        for ev in events:
            d_str = ev['date']
            d_obj = date.fromisoformat(d_str)
            day_idx = (d_obj - week_start).days
            
            start_t = ev.get('start_time')
            end_t = ev.get('end_time')
            
            if start_t and day_idx >= 0 and day_idx < 7:
                # Find matching blocks
                # e.g. start_t = '08:00:00' -> block 1
                for b in time_blocks:
                    b_start = b['start'] + ':00'
                    b_end = b['end'] + ':00'
                    if (start_t <= b_start and end_t >= b_end) or (start_t == b_start):
                        grid[b['num']][day_idx].append(ev)
            elif day_idx >= 0 and day_idx < 7:
                all_day_events[day_idx].append(ev)

        context.update({
            'active_nav': 'dashboard',
            'week_title': week_title,
            'days_of_week': days_of_week,
            'time_blocks': time_blocks,
            'grid': grid,
            'all_day_events': all_day_events,
            'prev_week_url': reverse('ui-calendar-week', args=[prev_week.year, prev_week.month, prev_week.day]),
            'next_week_url': reverse('ui-calendar-week', args=[next_week.year, next_week.month, next_week.day]),
            'today': timezone.localdate(),
        })
        return context
