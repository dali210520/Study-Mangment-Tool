import re

def update_templates():
    js_and_html = '''
<!-- CSRF Token for fetch API -->
<form style="display:none;">{% csrf_token %}</form>

<!-- Custom Context Menu for Events -->
<div id="eventContextMenu" style="display:none; position:absolute; z-index:2000; background:var(--surface); border:1px solid var(--border); box-shadow:0 4px 12px rgba(0,0,0,0.15); border-radius:6px; overflow:hidden; min-width:150px;">
    <a href="#" id="ctxCopyBtn" style="display:block; padding:10px 16px; text-decoration:none; color:var(--text); font-weight:500; font-size:14px; border-bottom:1px solid var(--border-soft);">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:8px; vertical-align:middle;"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
        Kopieren
    </a>
</div>

<!-- Custom Context Menu for Empty Cells -->
<div id="cellContextMenu" style="display:none; position:absolute; z-index:2000; background:var(--surface); border:1px solid var(--border); box-shadow:0 4px 12px rgba(0,0,0,0.15); border-radius:6px; overflow:hidden; min-width:150px;">
    <a href="#" id="ctxPasteBtn" style="display:block; padding:10px 16px; text-decoration:none; color:var(--text); font-weight:500; font-size:14px;">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:8px; vertical-align:middle;"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>
        Einfügen
    </a>
</div>

<script>
// CSRF Helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken') || document.querySelector('[name=csrfmiddlewaretoken]').value;

// Drag and Drop
function handleDragStart(e) {
    e.dataTransfer.setData('text/plain', JSON.stringify({
        id: e.target.getAttribute('data-id'),
        type: e.target.getAttribute('data-type')
    }));
    e.target.style.opacity = '0.5';
}

function handleDragEnd(e) {
    e.target.style.opacity = '1';
}

function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
}

function handleDrop(e, newDate, newTime) {
    e.preventDefault();
    try {
        const data = JSON.parse(e.dataTransfer.getData('text/plain'));
        if (!data.id || !data.type) return;

        fetch("{% url 'ui-api-event-move' %}", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                event_type: data.type,
                event_id: data.id,
                new_date: newDate,
                new_time: newTime || null
            })
        }).then(res => res.json()).then(result => {
            if (result.status === 'success') {
                window.location.reload();
            } else {
                alert('Fehler beim Verschieben: ' + result.error);
            }
        });
    } catch(err) {
        console.error(err);
    }
}

// Context Menu (Copy/Paste)
let copiedEvent = null;
let cellContextTarget = null;

document.addEventListener('click', () => {
    document.getElementById('eventContextMenu').style.display = 'none';
    document.getElementById('cellContextMenu').style.display = 'none';
});

function handleEventContextMenu(e, id, type) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('cellContextMenu').style.display = 'none';
    const menu = document.getElementById('eventContextMenu');
    menu.style.display = 'block';
    menu.style.left = e.pageX + 'px';
    menu.style.top = e.pageY + 'px';
    
    document.getElementById('ctxCopyBtn').onclick = function(ev) {
        ev.preventDefault();
        copiedEvent = { id, type };
        menu.style.display = 'none';
        
        // Show small toast or visual feedback if desired
    };
}

function handleCellContextMenu(e, newDate, newTime) {
    if (!copiedEvent) return; // Only show if something is copied
    e.preventDefault();
    document.getElementById('eventContextMenu').style.display = 'none';
    const menu = document.getElementById('cellContextMenu');
    menu.style.display = 'block';
    menu.style.left = e.pageX + 'px';
    menu.style.top = e.pageY + 'px';

    document.getElementById('ctxPasteBtn').onclick = function(ev) {
        ev.preventDefault();
        fetch("{% url 'ui-api-event-copy' %}", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                event_type: copiedEvent.type,
                event_id: copiedEvent.id,
                new_date: newDate,
                new_time: newTime || null
            })
        }).then(res => res.json()).then(result => {
            if (result.status === 'success') {
                window.location.reload();
            } else {
                alert('Fehler beim Einfügen: ' + result.error);
            }
        });
    };
}
</script>
'''

    def process_file(filepath, is_week=True):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Add data attributes and draggable to cal-event
        a_old = 'class="cal-event {{ ev.type }}"'
        a_new = 'class="cal-event {{ ev.type }}" data-id="{{ ev.id }}" data-type="{{ ev.type }}" draggable="true" ondragstart="handleDragStart(event)" ondragend="handleDragEnd(event)" oncontextmenu="handleEventContextMenu(event, \'{{ ev.id }}\', \'{{ ev.type }}\')"'
        content = content.replace(a_old, a_new)

        # Update calendar-cell for dragover and drop
        # Week view and Day view have different date variables
        date_var = "{{ day.date|date:'Y-m-d' }}" if is_week else "{{ target_date|date:'Y-m-d' }}"
        
        # 1. Block cells
        td_block_old = '<td class="calendar-cell {% if day.is_today %}today-col{% endif %}" onclick="openAddModal' if is_week else '<td class="calendar-cell" onclick="openAddModal'
        td_block_new = '<td class="calendar-cell {% if day.is_today %}today-col{% endif %}" ondragover="handleDragOver(event)" ondrop="handleDrop(event, \'' + date_var + '\', \'{{ block.start }}\')" oncontextmenu="handleCellContextMenu(event, \'' + date_var + '\', \'{{ block.start }}\')" onclick="openAddModal' if is_week else '<td class="calendar-cell" ondragover="handleDragOver(event)" ondrop="handleDrop(event, \'' + date_var + '\', \'{{ block.start }}\')" oncontextmenu="handleCellContextMenu(event, \'' + date_var + '\', \'{{ block.start }}\')" onclick="openAddModal'
        
        content = content.replace(td_block_old, td_block_new)

        # 2. All day cells
        if is_week:
            td_allday_old = '<td class="{% if day.is_today %}today-col{% endif %}" style="background:var(--surface-soft);">'
            td_allday_new = '<td class="{% if day.is_today %}today-col{% endif %}" style="background:var(--surface-soft);" ondragover="handleDragOver(event)" ondrop="handleDrop(event, \'' + date_var + '\', \'\')" oncontextmenu="handleCellContextMenu(event, \'' + date_var + '\', \'\')">'
            content = content.replace(td_allday_old, td_allday_new)
        else:
            td_allday_old = '<td style="background:var(--surface-soft);">'
            td_allday_new = '<td style="background:var(--surface-soft);" ondragover="handleDragOver(event)" ondrop="handleDrop(event, \'' + date_var + '\', \'\')" oncontextmenu="handleCellContextMenu(event, \'' + date_var + '\', \'\')">'
            content = content.replace(td_allday_old, td_allday_new)

        if 'handleDragStart' not in content:
            content = content.replace('{% endblock %}', js_and_html + '\n{% endblock %}')

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    process_file('templates/ui/calendar_week.html', is_week=True)
    process_file('templates/ui/calendar_day.html', is_week=False)

update_templates()
