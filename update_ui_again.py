import re
import glob

def remove_all_day_row(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # We need to remove the <tr> block that contains "Aufgaben &<br>Prüfungen"
    # Find the start of the tr and end of the tr
    if 'Aufgaben &<br>Prüfungen' in content:
        # Regex to remove the <tr> ... </tr> that contains Aufgaben &<br>Prüfungen
        content = re.sub(r'<tr>\s*<td class="time-col"[^>]*>Aufgaben &<br>Prüfungen</td>.*?</tr>', '', content, flags=re.DOTALL)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def update_colors(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Change .cal-event.task to green
    content = re.sub(r'\.cal-event\.task\s*\{.*?\}', '.cal-event.task { background: #e8f7ea; border: 1px solid #28a745; color: #155724; }', content)
    
    # Change .cal-event.deadline to red
    content = re.sub(r'\.cal-event\.deadline\s*\{.*?\}', '.cal-event.deadline { background: #f8d7da; border: 1px solid #dc3545; color: #721c24; }', content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

# Apply changes
remove_all_day_row('templates/ui/calendar_week.html')
remove_all_day_row('templates/ui/calendar_day.html')

for template in ['templates/ui/calendar.html', 'templates/ui/calendar_week.html', 'templates/ui/calendar_day.html']:
    update_colors(template)
