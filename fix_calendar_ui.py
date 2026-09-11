import re

def update_week_html():
    with open('templates/ui/calendar_week.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Restore the All Day Row, but renamed
    all_day_row = '''
            <tr>
                <td class="time-col" style="vertical-align: middle;">Aufgaben &<br>Prüfungen</td>
                {% for day in days_of_week %}
                    <td class="{% if day.is_today %}today-col{% endif %}" style="background:var(--surface-soft);">
                        {% for d_idx, ev_list in all_day_events.items %}
                            {% if d_idx == day.col_idx %}
                                {% for ev in ev_list %}
                                    <a href="{% if ev.type == 'lecture' %}{% url 'ui-lecture-update' ev.id %}{% elif ev.type == 'task' %}{% url 'ui-task-update' ev.id %}{% elif ev.type == 'deadline' %}{% url 'ui-deadline-update' ev.id %}{% elif ev.type == 'study_plan' %}{% url 'ui-plan-update' ev.id %}{% else %}#{% endif %}" class="cal-event {{ ev.type }}" title="{{ ev.title }}" onclick="event.stopPropagation();">
                                        {{ ev.title }}
                                    </a>
                                {% endfor %}
                            {% endif %}
                        {% endfor %}
                    </td>
                {% endfor %}
            </tr>
            '''
    
    if 'Aufgaben &<br>Prüfungen' not in content:
        # insert before first block loop
        content = content.replace('{% for block in time_blocks %}', all_day_row + '\n            {% for block in time_blocks %}')

    # Update cell onclick to use JS modal
    td_old = '<td class="calendar-cell {% if day.is_today %}today-col{% endif %}" onclick="window.location.href=\'{% url \'ui-lecture-create-global\' %}?date={{ day.date|date:\'Y-m-d\' }}&time={{ block.start }}\'">'
    td_new = '<td class="calendar-cell {% if day.is_today %}today-col{% endif %}" onclick="openAddModal(\'{{ day.date|date:\'Y-m-d\' }}\', \'{{ block.start }}\')">'
    content = content.replace(td_old, td_new)

    # Add Modal HTML and JS at the end of content block
    modal_html = '''
<!-- Add Event Modal -->
<div id="addEventModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:1000; align-items:center; justify-content:center;">
    <div style="background:var(--surface); padding:32px; border-radius:12px; text-align:center; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border: 1px solid var(--border);">
        <h3 style="margin-top:0; margin-bottom: 24px;">Was möchtest du hinzufügen?</h3>
        
        <div style="display:flex; gap:16px; justify-content:center; margin-bottom: 24px;">
            <a id="btnVorlesung" href="#" class="primary-button" style="background:var(--purple); border-color:var(--purple);">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 6px; vertical-align: middle;"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                Vorlesung
            </a>
            <a id="btnAufgabe" href="#" class="primary-button" style="background:var(--green); border-color:var(--green);">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 6px; vertical-align: middle;"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                Aufgabe
            </a>
        </div>
        
        <a href="#" onclick="document.getElementById('addEventModal').style.display='none'; return false;" style="color:var(--muted); text-decoration:none; font-weight:bold;">Abbrechen</a>
    </div>
</div>

<script>
function openAddModal(date, time) {
    document.getElementById('addEventModal').style.display = 'flex';
    document.getElementById('btnVorlesung').href = "{% url 'ui-lecture-create-global' %}?date=" + date + "&time=" + time;
    document.getElementById('btnAufgabe').href = "{% url 'ui-task-create' %}?date=" + date;
}
</script>
'''
    if 'addEventModal' not in content:
        content = content.replace('{% endblock %}', modal_html + '\n{% endblock %}')

    with open('templates/ui/calendar_week.html', 'w', encoding='utf-8') as f:
        f.write(content)

def update_day_html():
    with open('templates/ui/calendar_day.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Restore the All Day Row
    all_day_row = '''
            <tr>
                <td class="time-col" style="vertical-align: middle;">Aufgaben &<br>Prüfungen</td>
                <td style="background:var(--surface-soft);">
                    {% for ev in all_day_events %}
                        <a href="{% if ev.type == 'lecture' %}{% url 'ui-lecture-update' ev.id %}{% elif ev.type == 'task' %}{% url 'ui-task-update' ev.id %}{% elif ev.type == 'deadline' %}{% url 'ui-deadline-update' ev.id %}{% elif ev.type == 'study_plan' %}{% url 'ui-plan-update' ev.id %}{% else %}#{% endif %}" class="cal-event {{ ev.type }}" title="{{ ev.title }}" onclick="event.stopPropagation();">
                            {{ ev.title }}
                        </a>
                    {% empty %}
                        <span style="color: var(--muted); font-size: 12px;">Keine Aufgaben/Prüfungen</span>
                    {% endfor %}
                </td>
            </tr>
            '''
    
    if 'Aufgaben &<br>Prüfungen' not in content:
        content = content.replace('{% for block in time_blocks %}', all_day_row + '\n            {% for block in time_blocks %}')

    td_old_day = '<td class="calendar-cell" onclick="window.location.href=\'{% url \'ui-lecture-create-global\' %}?date={{ target_date|date:\'Y-m-d\' }}&time={{ block.start }}\'">'
    td_new_day = '<td class="calendar-cell" onclick="openAddModal(\'{{ target_date|date:\'Y-m-d\' }}\', \'{{ block.start }}\')">'
    content = content.replace(td_old_day, td_new_day)

    modal_html = '''
<!-- Add Event Modal -->
<div id="addEventModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:1000; align-items:center; justify-content:center;">
    <div style="background:var(--surface); padding:32px; border-radius:12px; text-align:center; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border: 1px solid var(--border);">
        <h3 style="margin-top:0; margin-bottom: 24px;">Was möchtest du hinzufügen?</h3>
        
        <div style="display:flex; gap:16px; justify-content:center; margin-bottom: 24px;">
            <a id="btnVorlesung" href="#" class="primary-button" style="background:var(--purple); border-color:var(--purple);">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 6px; vertical-align: middle;"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                Vorlesung
            </a>
            <a id="btnAufgabe" href="#" class="primary-button" style="background:var(--green); border-color:var(--green);">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 6px; vertical-align: middle;"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                Aufgabe
            </a>
        </div>
        
        <a href="#" onclick="document.getElementById('addEventModal').style.display='none'; return false;" style="color:var(--muted); text-decoration:none; font-weight:bold;">Abbrechen</a>
    </div>
</div>

<script>
function openAddModal(date, time) {
    document.getElementById('addEventModal').style.display = 'flex';
    document.getElementById('btnVorlesung').href = "{% url 'ui-lecture-create-global' %}?date=" + date + "&time=" + time;
    document.getElementById('btnAufgabe').href = "{% url 'ui-task-create' %}?date=" + date;
}
</script>
'''
    if 'addEventModal' not in content:
        content = content.replace('{% endblock %}', modal_html + '\n{% endblock %}')

    with open('templates/ui/calendar_day.html', 'w', encoding='utf-8') as f:
        f.write(content)

update_week_html()
update_day_html()
