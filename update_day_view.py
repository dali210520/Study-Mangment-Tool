import sys
import re

code = '''
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
'''

with open('apps/ui/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'class CalendarDayView.*?return context\n', code, content, flags=re.DOTALL)

with open('apps/ui/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
