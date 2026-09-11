import re

def modify_templates():
    # 1. Update calendar_week.html
    with open('templates/ui/calendar_week.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove add-event-btn CSS
    css_to_remove = '''    .add-event-btn {
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
    }'''
    content = content.replace(css_to_remove, '')

    # Update calendar-cell CSS
    old_cell_css = '''    .calendar-cell {
        position: relative;
    }'''
    new_cell_css = '''    .calendar-cell {
        cursor: pointer;
        transition: background 0.2s;
    }
    .calendar-cell:hover {
        background: var(--surface-soft);
    }'''
    content = content.replace(old_cell_css, new_cell_css)

    # Remove the <a> tag for add-event-btn
    btn_tag = '''<a href="{% url 'ui-lecture-create-global' %}?date={{ day.date|date:'Y-m-d' }}&time={{ block.start }}" class="add-event-btn" title="Vorlesung hier hinzufügen">+</a>\n                        '''
    content = content.replace(btn_tag, '')

    # Add onclick to td
    td_old = '<td class="calendar-cell {% if day.is_today %}today-col{% endif %}">'
    td_new = '<td class="calendar-cell {% if day.is_today %}today-col{% endif %}" onclick="window.location.href=\'{% url \'ui-lecture-create-global\' %}?date={{ day.date|date:\'Y-m-d\' }}&time={{ block.start }}\'">'
    content = content.replace(td_old, td_new)

    # Add stopPropagation to events
    a_old = 'class="cal-event {{ ev.type }}"'
    a_new = 'class="cal-event {{ ev.type }}" onclick="event.stopPropagation();"'
    content = content.replace(a_old, a_new)

    with open('templates/ui/calendar_week.html', 'w', encoding='utf-8') as f:
        f.write(content)

    # 2. Update calendar_day.html
    with open('templates/ui/calendar_day.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace(css_to_remove, '')
    content = content.replace(old_cell_css, new_cell_css)

    btn_tag_day = '''<a href="{% url 'ui-lecture-create-global' %}?date={{ target_date|date:'Y-m-d' }}&time={{ block.start }}" class="add-event-btn" title="Vorlesung hier hinzufügen">+</a>\n                    '''
    content = content.replace(btn_tag_day, '')

    td_old_day = '<td class="calendar-cell">'
    td_new_day = '<td class="calendar-cell" onclick="window.location.href=\'{% url \'ui-lecture-create-global\' %}?date={{ target_date|date:\'Y-m-d\' }}&time={{ block.start }}\'">'
    content = content.replace(td_old_day, td_new_day)

    content = content.replace(a_old, a_new)

    with open('templates/ui/calendar_day.html', 'w', encoding='utf-8') as f:
        f.write(content)

modify_templates()
