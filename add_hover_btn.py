import re

def add_hover_btn(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    css = '''
    .calendar-cell {
        position: relative;
    }
    .add-event-btn {
        display: none;
        position: absolute;
        bottom: 2px;
        right: 2px;
        background: var(--purple);
        color: white;
        width: 18px;
        height: 18px;
        border-radius: 50%;
        text-align: center;
        line-height: 16px;
        font-size: 14px;
        text-decoration: none;
        opacity: 0.3;
        z-index: 10;
        border: 1px solid var(--purple);
    }
    .calendar-cell:hover .add-event-btn {
        display: block;
    }
    .add-event-btn:hover {
        opacity: 1;
        background: #5532ad;
    }
'''
    if '.calendar-cell {' not in content:
        content = content.replace('</style>', css + '</style>')

    # In week view:
    td_week = '<td class="{% if day.is_today %}today-col{% endif %}">'
    td_week_new = '<td class="calendar-cell {% if day.is_today %}today-col{% endif %}">\n                        <a href="{% url \'ui-lecture-create-global\' %}?date={{ day.date|date:\'Y-m-d\' }}&time={{ block.start }}" class="add-event-btn" title="Vorlesung hier hinzufügen">+</a>'
    
    if td_week in content:
        content = content.replace(td_week, td_week_new)

    # In day view:
    td_day = '<td>\n                    {% for b_idx, ev_list in grid.items %}'
    td_day_new = '<td class="calendar-cell">\n                    <a href="{% url \'ui-lecture-create-global\' %}?date={{ target_date|date:\'Y-m-d\' }}&time={{ block.start }}" class="add-event-btn" title="Vorlesung hier hinzufügen">+</a>\n                    {% for b_idx, ev_list in grid.items %}'
    
    if td_day in content:
        content = content.replace(td_day, td_day_new)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

add_hover_btn('templates/ui/calendar_week.html')
add_hover_btn('templates/ui/calendar_day.html')
