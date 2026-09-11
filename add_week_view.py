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
                'is_today': d == timezone.localdate()
            })
            
        # Group events by date isoformat
        events_by_date = {}
        for ev in events:
            d_str = ev['date']
            events_by_date.setdefault(d_str, []).append(ev)
            
        context.update({
            'active_nav': 'dashboard',
            'week_title': week_title,
            'days_of_week': days_of_week,
            'events_by_date': events_by_date,
            'prev_week_url': reverse('ui-calendar-week', args=[prev_week.year, prev_week.month, prev_week.day]),
            'next_week_url': reverse('ui-calendar-week', args=[next_week.year, next_week.month, next_week.day]),
            'today': timezone.localdate(),
        })
        return context
'''

with open('apps/ui/views.py', 'a', encoding='utf-8') as f:
    f.write(code)
