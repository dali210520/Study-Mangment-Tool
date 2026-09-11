import re

def fix_template(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add table-layout: fixed
    content = content.replace('border-collapse: collapse;', 'border-collapse: collapse;\n        table-layout: fixed;')
    
    # Replace href="#" for cal-events
    href_logic = '''href="{% if ev.type == 'lecture' %}{% url 'ui-lecture-update' ev.id %}{% elif ev.type == 'task' %}{% url 'ui-task-update' ev.id %}{% elif ev.type == 'deadline' %}{% url 'ui-deadline-update' ev.id %}{% elif ev.type == 'study_plan' %}{% url 'ui-plan-update' ev.id %}{% else %}#{% endif %}"'''
    content = content.replace('href="#" class="cal-event', href_logic + ' class="cal-event')
    
    # Add create buttons
    create_btns = '''
        <a class="primary-button" href="{% url 'ui-task-create' %}" style="background: var(--green); border-color: var(--green); margin-right: 8px;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 4px; vertical-align: middle;"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
            Aufgabe
        </a>
        <a class="primary-button" href="{% url 'ui-lecture-create-global' %}" style="background: var(--purple); border-color: var(--purple); margin-right: 8px;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 4px; vertical-align: middle;"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
            Vorlesung
        </a>
    '''
    
    if '<div class="page-actions">' in content and 'DaVinci Import' in content:
        content = content.replace('<div class="page-actions">', '<div class="page-actions">\n' + create_btns)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

fix_template('templates/ui/calendar_week.html')
fix_template('templates/ui/calendar_day.html')
