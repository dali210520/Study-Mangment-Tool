import requests
from bs4 import BeautifulSoup
from datetime import datetime
from apps.courses.models import StudyModule, Lecture

def import_davinci_schedule(url, user):
    """
    Fetches a daVinci schedule URL, parses the timetable, and creates
    StudyModules and Lectures for the given user.
    """
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', class_='timetable')
    if not table:
        raise ValueError("Keine Stundenplan-Tabelle (timetable) auf der Seite gefunden.")
        
    # Extract days
    days = []
    thead = table.find('thead')
    if thead:
        header_row = thead.find('tr')
        if header_row:
            for th in header_row.find_all('th')[1:]:  # skip the first empty corner
                day_div = th.find('div', class_='day')
                if day_div:
                    # Expecting format like "Mon 29.06.26"
                    text = day_div.text.strip()
                    parts = text.split()
                    if len(parts) >= 2:
                        date_str = parts[1]
                        try:
                            # 2-digit year vs 4-digit year handling
                            fmt = "%d.%m.%Y" if len(date_str.split('.')[-1]) == 4 else "%d.%m.%y"
                            date_obj = datetime.strptime(date_str, fmt).date()
                            days.append(date_obj)
                        except ValueError:
                            pass
                            
    if not days:
        raise ValueError("Tage im Stundenplan konnten nicht erkannt werden.")

    # Parse grid with colspans and rowspans
    grid = {}
    row_idx = 0
    # Also search inside tbody if present, or direct trs
    rows = table.find_all('tr')
    for tr in rows:
        if tr.parent.name == 'thead':
            continue
        cells = tr.find_all(['td', 'th'], recursive=False)
        if not cells:
            continue
            
        col_idx = 0
        for cell in cells:
            while grid.get((row_idx, col_idx)) is not None:
                col_idx += 1
                
            rowspan = int(cell.get('rowspan', 1))
            colspan = int(cell.get('colspan', 1))
            
            for r in range(rowspan):
                for c in range(colspan):
                    grid[(row_idx + r, col_idx + c)] = cell
                    
            col_idx += colspan
        row_idx += 1
        
    # Extract events
    seen_cells = set()
    events_created = 0
    
    import re
    
    for (r, c), cell in grid.items():
        if cell in seen_cells:
            continue
        seen_cells.add(cell)
        
        if cell.name == 'td':
            day_idx = c - 1  # the first column is the time slot
            if 0 <= day_idx < len(days):
                date_obj = days[day_idx]
                
                # Extract time block from column 0
                start_time, end_time = None, None
                time_cell_start = grid.get((r, 0))
                if time_cell_start:
                    times = re.findall(r'(\d{2}:\d{2})', time_cell_start.get_text(separator=' '))
                    if len(times) >= 2:
                        start_time = datetime.strptime(times[0], '%H:%M').time()
                
                end_r = r + int(cell.get('rowspan', 1)) - 1
                time_cell_end = grid.get((end_r, 0))
                if time_cell_end:
                    times = re.findall(r'(\d{2}:\d{2})', time_cell_end.get_text(separator=' '))
                    if len(times) >= 2:
                        end_time = datetime.strptime(times[-1], '%H:%M').time()
                
                event_containers = cell.find_all('div', class_='event-container')
                for ev in event_containers:
                    subj_el = ev.find(class_='lesson-subject')
                    teach_el = ev.find(class_='lesson-teacher')
                    room_el = ev.find(class_='lesson-room')
                    
                    title = subj_el.text.strip() if subj_el else "Unbekanntes Fach"
                    t_txt = teach_el.text.strip() if teach_el else ""
                    r_txt = room_el.text.strip() if room_el else ""
                    
                    notes_parts = []
                    if t_txt:
                        notes_parts.append(f"Dozent: {t_txt}")
                    if r_txt:
                        notes_parts.append(f"Raum: {r_txt}")
                    notes = "\n".join(notes_parts)
                    
                    # Create or get Module
                    module_name = title
                    # optionally clean up title (e.g. remove " (V)" or " (Ü)")
                    if module_name.endswith("(V)") or module_name.endswith("(Ü)") or module_name.endswith("(P)"):
                        module_name = module_name[:-3].strip()
                        
                    module, _ = StudyModule.objects.get_or_create(
                        user=user,
                        name=module_name,
                        defaults={
                            'lecturer': t_txt,
                            'description': 'Automatisch importiert aus daVinci.'
                        }
                    )
                    
                    # Create or Update Lecture (update times if it exists without times)
                    lecture = Lecture.objects.filter(module=module, date=date_obj, title=title).first()
                    if not lecture:
                        Lecture.objects.create(
                            module=module,
                            title=title,
                            date=date_obj,
                            start_time=start_time,
                            end_time=end_time,
                            notes=notes
                        )
                        events_created += 1
                    else:
                        # Update times if missing
                        updated = False
                        if start_time and not lecture.start_time:
                            lecture.start_time = start_time
                            updated = True
                        if end_time and not lecture.end_time:
                            lecture.end_time = end_time
                            updated = True
                        if updated:
                            lecture.save()
                        
    return events_created
