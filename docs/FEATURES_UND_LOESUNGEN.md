# Feature-Übersicht und Lösungen

Diese Datei beschreibt den aktuellen Funktionsstand des Study-Management-Tools,
die wichtigsten technischen Lösungen und die grobe Architektur. Sie ist bewusst
als einfache Projektdokumentation geschrieben, damit auch neue Teammitglieder
schnell verstehen, was das System aktuell kann.

## Aktueller Stand

Das Projekt ist ein modularer Django-Monolith für die Organisation eines Studiums.
Die Anwendung hat eine REST-API und eine serverseitig gerenderte Weboberfläche mit
Django Templates.

Aktuell umgesetzt:

- Benutzerkonto und Authentifizierung
- Dashboard als zentrale Startseite
- Module und Vorlesungen
- Aufgabenmanagement
- Abgaben und Prüfungen
- Lernpläne
- Fortschrittsübersicht und Kalenderdaten
- PDF-Unterlagen mit Textextraktion
- Suche und Filter
- Qualitätssicherung durch automatisierte Tests

## Features und Lösungen

### Benutzerkonto und Authentifizierung

Nutzer können sich registrieren, anmelden, abmelden und ihre Session verwenden.
Die Authentifizierung gibt es sowohl über die API als auch über normale UI-Seiten.

Lösung:

- Custom User Model in `apps/accounts/`
- Django Sessions für die Weboberfläche
- REST-Endpunkte für Registrierung, Login, Logout und User-Info
- Geschützte UI-Seiten, die nur angemeldete Nutzer sehen können

Wichtige Seiten:

- `/login/`
- `/register/`
- `/logout/`
- `/dashboard/`

### Dashboard

Das Dashboard ist die zentrale Übersicht nach dem Login. Es zeigt wichtige Zahlen
und kommende Punkte aus verschiedenen Bereichen.

Lösung:

- Daten werden aus den bestehenden Apps zusammengeführt
- Dashboard nutzt nur Daten des angemeldeten Nutzers
- Fortschritt, offene Aufgaben, überfällige Punkte und Lernzeit werden verdichtet
- Navigation führt auf echte Fachseiten statt auf Platzhalter

Wichtige Datei:

- `templates/ui/dashboard.html`

### Module und Vorlesungen

Nutzer können Studienmodule und dazugehörige Vorlesungen verwalten. Vorlesungen
sind einem Modul zugeordnet.

Lösung:

- Fachlogik in `apps/courses/`
- Module und Vorlesungen als eigene Models
- API mit CRUD-Funktionen
- UI-Seiten für Listen, Details, Erstellen, Bearbeiten und Löschen
- Suche, Filter und Sortierung

Wichtige Bereiche:

- `apps/courses/`
- `apps/ui/course_views.py`
- `templates/ui/modules/`
- `templates/ui/lectures/`

### Aufgabenmanagement

Aufgaben können erstellt, gefiltert, bearbeitet, gelöscht und schnell im Status
geändert werden.

Lösung:

- Aufgaben liegen in `apps/tasks/`
- Status, Priorität, Fälligkeit und optionaler Modulbezug
- Automatisches Erledigungsdatum, wenn eine Aufgabe abgeschlossen wird
- UI-Filter nach Status, Priorität, Modul und Fälligkeit
- Überfällige Aufgaben werden erkennbar gemacht

Wichtige Bereiche:

- `apps/tasks/`
- `apps/ui/task_views.py`
- `templates/ui/tasks/`

### Abgaben und Prüfungen

Das System kann Abgaben, Prüfungen, Präsentationen, Projekte und weitere Termine
verwalten.

Lösung:

- Termine liegen in `apps/deadlines/`
- Typ, Status, Datum, Notizen und optionaler Modulbezug
- Schneller Statuswechsel aus der Liste
- Filter nach Typ, Status, Modul und Datum
- Überfällige Termine werden markiert

Wichtige Bereiche:

- `apps/deadlines/`
- `apps/ui/deadline_views.py`
- `templates/ui/deadlines/`

### Lernpläne

Lernplan-Einträge helfen dabei, Lernzeit nach Thema, Modul und Termin zu planen.

Lösung:

- Lernpläne liegen in `apps/plans/`
- Einträge haben Thema, Datum, Dauer, Status und optionalen Bezug zu Modul oder Deadline
- UI mit Suche, Filtern, Bearbeiten, Löschen und schnellem Statuswechsel
- Vergangene offene Lerneinheiten werden hervorgehoben

Wichtige Bereiche:

- `apps/plans/`
- `apps/ui/plan_views.py`
- `templates/ui/plans/`

### Fortschritt und Auswertung

Die Fortschrittsseite zeigt, wie viele Aufgaben erledigt sind, wie viel Lernzeit
geschafft wurde und welche Punkte bald anstehen.

Lösung:

- Gemeinsame Auswertungslogik in `apps/overview/services.py`
- API für Fortschrittsdaten und Kalenderdaten
- UI-Seite für Aufgaben-, Termin- und Lernzeit-Auswertung
- Kalenderdaten kombinieren Vorlesungen, Aufgaben, Deadlines und Lernpläne

Wichtige Bereiche:

- `apps/overview/`
- `apps/ui/progress_views.py`
- `templates/ui/progress/`

### PDF-Unterlagen und Suche

PDF-Unterlagen können hochgeladen, einem Modul zugeordnet und durchsucht werden.
Beim Upload wird Text aus der PDF extrahiert.

Lösung:

- Materialverwaltung in `apps/materials/`
- Datei-Metadaten, Seitenanzahl und extrahierter Text werden gespeichert
- Textextraktion über `pypdf`
- Suchseite zeigt Treffer mit Snippet
- Suchergebnis kann die echte Datei Öffnen oder den Materialeintrag bearbeiten

Wichtige Bereiche:

- `apps/materials/`
- `apps/materials/services.py`
- `apps/ui/material_views.py`
- `templates/ui/materials/`
- `templates/ui/search/`

### Suche, Filter und Komfortfunktionen

Fast alle Fachbereiche haben Such-, Filter- und Sortiermöglichkeiten. Dadurch wird
die Anwendung nicht nur zur Datenerfassung, sondern auch zur schnellen Arbeitsoberfläche.

Lösung:

- API-Filter für Status, Datum, Modul, Typ und Sortierung
- Gemeinsame Validierung für Query-Parameter in `apps/core/query_params.py`
- UI-Filter bleiben bewusst einfach und direkt sichtbar
- Ungültige API-Parameter liefern kontrollierte Fehler statt unklarer Serverfehler

## Architektur

Das Projekt ist nach Fachbereichen getrennt:

- `apps/accounts/` für Nutzer und Authentifizierung
- `apps/core/` für Health Check, API-Info und gemeinsame Query-Helfer
- `apps/courses/` für Module und Vorlesungen
- `apps/tasks/` für Aufgaben
- `apps/deadlines/` für Abgaben und Prüfungen
- `apps/plans/` für Lernpläne
- `apps/overview/` für Auswertung und Kalender
- `apps/materials/` für PDF-Unterlagen
- `apps/ui/` für serverseitige UI-Views und Formulare
- `templates/` für HTML-Templates
- `tests/` für automatisierte Tests

Die wichtigste Architekturentscheidung ist die Trennung zwischen API-Apps und
UI-Schicht. Die Fach-Apps enthalten Models, Serializer und API-Views. Die UI-App
verwendet diese Daten für normale Webseiten. Dadurch kann später trotzdem noch
ein modernes Frontend oder eine mobile App auf die API zugreifen.

## Teststruktur

Das Projekt nutzt `pytest` mit `pytest-django`. Die Einstellungen liegen in
`pytest.ini`.

Wichtige Test-Konfiguration:

- `DJANGO_SETTINGS_MODULE = config.settings`
- Tests liegen im Ordner `tests/`
- Testdateien heißen `test_*.py`
- Testklassen beginnen mit `Test`
- Testfunktionen beginnen mit `test_`
- Standardlauf erzeugt Coverage für `apps/`

### Markierungen

In `pytest.ini` sind Marker definiert:

- `unit` für Model- und kleinere Logiktests
- `integration` für API- und UI-Tests mit Datenbankzugriff
- `authentication` für Login, Logout und Registrierung
- `slow` als Reserve für langsamere Tests

Beispiele:

```bash
pytest -m unit
pytest -m integration
pytest -m authentication
```

### Gemeinsame Fixtures

In `conftest.py` liegen gemeinsame Testdaten:

- `user_data` für gültige Registrierungsdaten
- `invalid_user_data` für ungültige Registrierungsdaten
- `authenticated_user` für einen fertig angelegten Testnutzer

Einzelne Testdateien haben zusätzlich eigene Fixtures, wenn sie spezielle Daten
brauchen, zum Beispiel Module, Aufgaben, Deadlines oder Materialien.

### Testbereiche

Die Tests sind nach Fachbereich und Schicht getrennt:

- `test_auth_api.py`, `test_login.py`, `test_registration.py` prüfen Auth per API
- `test_auth_ui.py` prüft Login- und Registrierungsseiten
- `test_courses_models.py` prüft Modul- und Vorlesungsmodels
- `test_courses_api.py` prüft die Modul- und Vorlesungs-API
- `test_courses_ui.py` prüft die Modul- und Vorlesungsseiten
- `test_tasks_models.py`, `test_tasks_api.py`, `test_tasks_ui.py` prüfen Aufgaben
- `test_deadlines_models.py`, `test_deadlines_api.py`, `test_deadlines_ui.py` prüfen Termine
- `test_plans_models.py`, `test_plans_api.py`, `test_plans_ui.py` prüfen Lernpläne
- `test_materials_models.py`, `test_materials_api.py` prüfen PDF-Unterlagen
- `test_overview_api.py` prüft Fortschritt und Kalender-API
- `test_dashboard_ui.py` prüft Dashboard-Daten und Zugriff
- `test_query_param_validation.py` prüft robuste Filtervalidierung
- `test_core_api.py` prüft Health Check und API-Info
- `test_final_ui.py` prüft Fortschritt, PDF-Unterlagen und Suchseiten
- `test_smoke.py` ist ein sehr kleiner Pipeline-Test

### Wie man die Tests laufen lässt

Alle Tests:

```bash
pytest
```

Ausführlicher:

```bash
pytest -v
```

Nur Authentifizierung:

```bash
pytest -m authentication
```

Nur eine Datei:

```bash
pytest tests/test_tasks_ui.py
```

Mit Coverage:

```bash
pytest --cov=apps --cov-report=html --cov-report=term-missing
```

Danach liegt der HTML-Coverage-Report normalerweise in `htmlcov/`.

## Was die Teststruktur absichert

Die Teststruktur prüft nicht nur, ob Seiten erreichbar sind. Sie sichert auch ab,
dass Nutzer nur ihre eigenen Daten sehen, dass Filter korrekt funktionieren, dass
CRUD-Aktionen arbeiten und dass ungültige Eingaben kontrolliert behandelt werden.

Dadurch ist das Projekt gut vorbereitet für weiteres UI-Design, weil die Kernlogik
bereits durch Tests geschützt ist.
