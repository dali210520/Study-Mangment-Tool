import sys

code = '''
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
'''
import re
with open('apps/ui/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'class CalendarWeekView.*?return context\n', code, content, flags=re.DOTALL)

with open('apps/ui/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
