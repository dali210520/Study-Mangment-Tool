## Study-Management-Tool

> Ein modulares Django-basiertes System zur Organisation des gesamten Studiums

### 📋 Projekt-Status

| Issue | Feature | Status |
|-------|---------|--------|
| #4 | Authentifizierung (Registrierung & Login) | ✅ DONE |
| - | Module & Vorlesungen | ✅ DONE |
| - | Aufgabenmanagement | ✅ DONE |
| - | Abgaben & Prüfungen | ✅ DONE |
| - | Lernpläne | ✅ DONE |
| - | Fortschrittsübersicht & Kalender-API | ✅ DONE |
| - | Suche, Filter & Komfortfunktionen | ✅ DONE |
| - | PDF-Unterlagen | ✅ DONE |
| - | Qualität, Stabilisierung & UI-Vorbereitung | ✅ DONE |
| - | Dashboard-UI | ✅ DONE |

---

## 🛠️ Tech Stack

- **Backend:** Python 3.14 / Django 4.2.13
- **API:** Django REST Framework 3.14
- **Database:** SQLite (Entwicklung) / PostgreSQL (Produktion)
- **Testing:** pytest >=8.0.0, pytest-django>=4.7.0
- **Authentication:** Django Sessions + Custom User Model
- **UI:** Django Templates
- **PDF:** pypdf 5.1
- **Configuration:** python-decouple für einfache Umgebungsvariablen

---

## 💡 Projektkonzept

Eine Web-Anwendung zur Organisation des gesamten Studiums:
- ✅ **Authentifizierung** - Benutzerregistrierung & Login per API und UI
- ✅ **Vorlesungen & Module** - Kurs-Management
- ✅ **Lernpläne** - Zeitplanung & Tracking
- ✅ **Abgaben & Prüfungen** - Deadline-Management
- ✅ **Fortschrittsübersicht** - Statistiken & Analytics
- ✅ **Aufgabenmanagement** - Task-Tracking
- ✅ **Suche & Filter** - Schneller Zugriff auf relevante Daten
- ✅ **PDF-Unterlagen** - Upload, Textextraktion & Suche
- ✅ **Qualität & Stabilisierung** - Health Check, API-Info und robuste Query-Validierung
- ✅ **Dashboard-UI** - Kennzahlen, Fortschritt und kommende Termine

---

## 🏗️ Architektur

**Modularer Django-Monolith mit Schichtenarchitektur**

**Implementiert:**
- Ein Django-Projekt (`config/`)
- Mehrere Django-Apps (in `apps/`)
- Klare Trennung nach Fachbereichen

**Apps:**
- `apps/ui/` - ✅ Dashboard und serverseitige UI-Seiten
- `apps/core/` - ✅ API-Info, Health Check & gemeinsame Query-Validierung
- `apps/accounts/` - ✅ Authentifizierung & Benutzerverwaltung
- `apps/courses/` - ✅ Module & Vorlesungen
- `apps/tasks/` - ✅ Aufgabenmanagement
- `apps/deadlines/` - ✅ Abgaben & Prüfungen
- `apps/plans/` - ✅ Lernpläne
- `apps/overview/` - ✅ Fortschritt & Kalender-API
- `apps/materials/` - ✅ PDF-Unterlagen

---

## 🚀 Schnellstart

### Voraussetzungen
- Python 3.9+ (getestet mit Python 3.14)
- pip / virtualenv

### 1. Projekt Setup

```bash
# Virtual Environment erstellen
python -m venv venv
venv\Scripts\activate  # Windows

# Dependencies installieren
pip install -r requirements.txt
```

### 2. Datenbank Setup

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 3. Optionale Konfiguration

Für die lokale Entwicklung funktionieren sinnvolle Standardwerte. Für andere Umgebungen können diese Variablen gesetzt werden:

```bash
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 4. Server starten

```bash
python manage.py runserver
```

Login läuft unter: http://localhost:8000/login/
Registrierung läuft unter: http://localhost:8000/register/
Dashboard läuft unter: http://localhost:8000/dashboard/
Admin läuft unter: http://localhost:8000/admin/

### 5. Tests ausführen

```bash
pytest -v
```

---

## ✅ Issue #4: Authentifizierung - IMPLEMENTIERT

### Features
- ✅ Benutzerregistrierung mit Validierung
- ✅ Benutzer-Login mit Session Management
- ✅ Custom User Model (Best Practice)
- ✅ REST API Endpoints
- ✅ Server-rendered Login- und Registrierungsseiten
- ✅ Django Admin Integration

### API Endpoints

```
POST   /api/auth/register/          # Registrierung
POST   /api/auth/login/             # Login
POST   /api/auth/logout/            # Logout
GET    /api/auth/me/                # Aktuelle User-Info
PUT    /api/auth/profile/update/    # Profil aktualisieren
```

### UI Endpoints

```
GET  /login/      # Nutzer-Login
POST /login/      # Nutzer anmelden
GET  /register/   # Registrierung anzeigen
POST /register/   # Nutzerkonto erstellen
POST /logout/     # Nutzer abmelden
```

---

## ✅ Module & Vorlesungen - IMPLEMENTIERT

### Features
- ✅ Module mit Name, Semester, Dozent und Beschreibung
- ✅ Vorlesungen mit Titel, Datum und Notizen
- ✅ Nutzer sehen und bearbeiten nur ihre eigenen Module
- ✅ Vorlesungen werden einem Modul zugeordnet
- ✅ Suche, Datumsfilter und Sortierung
- ✅ REST API Endpoints
- ✅ Server-rendered UI-Seiten für Module und Vorlesungen
- ✅ Modul- und Vorlesungs-CRUD über die Weboberfläche
- ✅ Sidebar-Navigation führt auf echte Seiten statt API-Platzhalter
- ✅ Django Admin Integration
- ✅ Automatisierte Tests

### API Endpoints

```
GET    /api/modules/                       # Eigene Module anzeigen
POST   /api/modules/                       # Modul erstellen
GET    /api/modules/<id>/                  # Einzelnes Modul anzeigen
PATCH  /api/modules/<id>/                  # Modul bearbeiten
DELETE /api/modules/<id>/                  # Modul löschen
GET    /api/modules/<module_id>/lectures/  # Vorlesungen eines Moduls anzeigen
POST   /api/modules/<module_id>/lectures/  # Vorlesung erstellen
GET    /api/lectures/<id>/                 # Einzelne Vorlesung anzeigen
PATCH  /api/lectures/<id>/                 # Vorlesung bearbeiten
DELETE /api/lectures/<id>/                 # Vorlesung löschen
```

### UI Endpoints

```
GET  /modules/                              # Modulübersicht
GET  /modules/new/                          # Modul erstellen
GET  /modules/<id>/                         # Moduldetail mit Vorlesungen
GET  /modules/<id>/edit/                    # Modul bearbeiten
POST /modules/<id>/delete/                  # Modul löschen
GET  /lectures/                             # Alle Vorlesungen
GET  /modules/<module_id>/lectures/new/     # Vorlesung erstellen
GET  /lectures/<id>/edit/                   # Vorlesung bearbeiten
POST /lectures/<id>/delete/                 # Vorlesung löschen
```

### Suche, Filter & Sortierung

```
GET /api/modules/?search=sql
GET /api/modules/?ordering=-name
GET /api/modules/<module_id>/lectures/?search=testing
GET /api/modules/<module_id>/lectures/?date_before=2026-10-31
GET /api/modules/<module_id>/lectures/?ordering=-date
```

---

## ✅ Aufgabenmanagement - IMPLEMENTIERT

### Features
- ✅ Aufgaben mit Titel, Beschreibung, Priorität und Status
- ✅ Optionaler Modulbezug
- ✅ Fälligkeitsdatum
- ✅ Automatisches Erledigungsdatum bei Status `done`
- ✅ Suche, Filter und Sortierung
- ✅ Nutzer sehen und bearbeiten nur ihre eigenen Aufgaben
- ✅ REST API Endpoints
- ✅ Server-rendered UI-Seiten für Aufgaben
- ✅ Aufgaben-CRUD über die Weboberfläche
- ✅ Schneller Statuswechsel direkt aus der Aufgabenliste
- ✅ UI-Filter nach Status, Priorität, Modul und Fälligkeit
- ✅ Überfällige Aufgaben werden in der UI hervorgehoben
- ✅ Django Admin Integration
- ✅ Automatisierte Tests

### API Endpoints

```
GET    /api/tasks/              # Eigene Aufgaben anzeigen
POST   /api/tasks/              # Aufgabe erstellen
GET    /api/tasks/<id>/         # Einzelne Aufgabe anzeigen
PATCH  /api/tasks/<id>/         # Aufgabe bearbeiten
DELETE /api/tasks/<id>/         # Aufgabe löschen
```

### UI Endpoints

```
GET  /tasks/              # Aufgabenübersicht mit Suche und Filtern
GET  /tasks/new/          # Aufgabe erstellen
GET  /tasks/<id>/edit/    # Aufgabe bearbeiten
POST /tasks/<id>/status/  # Aufgabenstatus schnell ändern
POST /tasks/<id>/delete/  # Aufgabe löschen
```

### Filter

```
GET /api/tasks/?status=open
GET /api/tasks/?priority=high
GET /api/tasks/?module=<module_id>
GET /api/tasks/?due_before=2026-10-31
GET /api/tasks/?due_after=2026-10-01
GET /api/tasks/?due=overdue
GET /api/tasks/?due=next_7_days
GET /api/tasks/?search=sorting
GET /api/tasks/?ordering=priority
```

---

## ✅ Abgaben & Prüfungen - IMPLEMENTIERT

### Features
- ✅ Abgaben, Prüfungen, Präsentationen, Projekte und sonstige Termine
- ✅ Optionaler Modulbezug
- ✅ Datum, Status und Notizen
- ✅ Kennzeichnung vergangener Termine über `is_past_due`
- ✅ Suche, Filter und Sortierung
- ✅ Nutzer sehen und bearbeiten nur ihre eigenen Termine
- ✅ REST API Endpoints
- ✅ Server-rendered UI-Seiten für Abgaben & Prüfungen
- ✅ Termin-CRUD über die Weboberfläche
- ✅ Schneller Statuswechsel direkt aus der Terminliste
- ✅ UI-Filter nach Art, Status, Modul und Datum
- ✅ Überfällige Termine werden in der UI hervorgehoben
- ✅ Django Admin Integration
- ✅ Automatisierte Tests

### API Endpoints

```
GET    /api/deadlines/              # Eigene Abgaben & Prüfungen anzeigen
POST   /api/deadlines/              # Termin erstellen
GET    /api/deadlines/<id>/         # Einzelnen Termin anzeigen
PATCH  /api/deadlines/<id>/         # Termin bearbeiten
DELETE /api/deadlines/<id>/         # Termin löschen
```

### UI Endpoints

```
GET  /deadlines/              # Terminübersicht mit Suche und Filtern
GET  /deadlines/new/          # Abgabe oder Prüfung erstellen
GET  /deadlines/<id>/edit/    # Termin bearbeiten
POST /deadlines/<id>/status/  # Terminstatus schnell ändern
POST /deadlines/<id>/delete/  # Termin löschen
```

### Filter

```
GET /api/deadlines/?type=exam
GET /api/deadlines/?status=upcoming
GET /api/deadlines/?module=<module_id>
GET /api/deadlines/?date_before=2026-12-31
GET /api/deadlines/?date_after=2026-10-01
GET /api/deadlines/?date=overdue
GET /api/deadlines/?date=next_7_days
GET /api/deadlines/?search=sql
GET /api/deadlines/?ordering=-date
```

---

## ✅ Lernpläne - IMPLEMENTIERT

### Features
- ✅ Lernplan-Einträge mit Thema, Datum, Dauer und Status
- ✅ Optionaler Modulbezug
- ✅ Optionaler Deadline-Bezug
- ✅ Suche, Filter und Sortierung
- ✅ Nutzer sehen und bearbeiten nur ihre eigenen Lernplan-Einträge
- ✅ REST API Endpoints
- ✅ Server-rendered UI-Seiten für Lernpläne
- ✅ Lernplan-CRUD über die Weboberfläche
- ✅ Schneller Statuswechsel direkt aus der Lernplanliste
- ✅ UI-Filter nach Status, Modul, Abgabe/Prüfung und Datum
- ✅ Vergangene offene Lerneinheiten werden in der UI hervorgehoben
- ✅ Django Admin Integration
- ✅ Automatisierte Tests

### API Endpoints

```
GET    /api/study-plans/              # Eigene Lernplan-Einträge anzeigen
POST   /api/study-plans/              # Lernplan-Eintrag erstellen
GET    /api/study-plans/<id>/         # Einzelnen Lernplan-Eintrag anzeigen
PATCH  /api/study-plans/<id>/         # Lernplan-Eintrag bearbeiten
DELETE /api/study-plans/<id>/         # Lernplan-Eintrag löschen
```

### UI Endpoints

```
GET  /study-plans/              # Lernplanübersicht mit Suche und Filtern
GET  /study-plans/new/          # Lernplan-Eintrag erstellen
GET  /study-plans/<id>/edit/    # Lernplan-Eintrag bearbeiten
POST /study-plans/<id>/status/  # Lernplanstatus schnell ändern
POST /study-plans/<id>/delete/  # Lernplan-Eintrag löschen
```

### Filter

```
GET /api/study-plans/?status=planned
GET /api/study-plans/?module=<module_id>
GET /api/study-plans/?deadline=<deadline_id>
GET /api/study-plans/?date_before=2026-12-01
GET /api/study-plans/?date_after=2026-11-01
GET /api/study-plans/?date=past
GET /api/study-plans/?date=next_7_days
GET /api/study-plans/?search=sql
GET /api/study-plans/?ordering=-duration
```

---

## ✅ Übersicht & Auswertung - IMPLEMENTIERT

### Features
- ✅ Fortschrittsübersicht als API
- ✅ Anzahl Module, Aufgaben, Deadlines und Lernplan-Einträge
- ✅ Offene, laufende und erledigte Aufgaben
- ✅ Kommende und überfällige Deadlines
- ✅ Geplante und erledigte Lernzeit in Minuten
- ✅ Kombinierte Kalender-API für Vorlesungen, Aufgaben, Deadlines und Lernpläne
- ✅ Zeitraum- und Modulfilter
- ✅ Nutzer sehen nur ihre eigenen Auswertungen
- ✅ Wiederverwendbare Service-Schicht für API und Dashboard
- ✅ Server-rendered Fortschrittsseite mit Aufgaben-, Termin- und Lernzeit-Auswertung
- ✅ Kommende Punkte aus dem Kalender werden in der UI angezeigt
- ✅ Automatisierte Tests

### API Endpoints

```
GET /api/progress/summary/      # Fortschrittsübersicht
GET /api/calendar/              # Kombinierte Kalender-/Eventliste
```

### UI Endpoints

```
GET /progress/                  # Fortschrittsübersicht
```

### Kalender-Filter

```
GET /api/calendar/?date_after=2026-10-01
GET /api/calendar/?date_before=2026-10-31
GET /api/calendar/?module=<module_id>
```

---

## ✅ Dashboard-UI - IMPLEMENTIERT

### Features
- ✅ Geschützte Dashboard-Seite für angemeldete Nutzer
- ✅ Root-Redirect von `/` auf `/dashboard/`
- ✅ Kennzahlen für Module, Aufgaben, überfällige Punkte und Lernzeit
- ✅ Fortschrittsbalken für erledigte Aufgaben und abgeschlossene Lernzeit
- ✅ Kommende Termine aus Vorlesungen, Aufgaben, Deadlines und Lernplänen
- ✅ Nutzer sehen nur ihre eigenen Dashboard-Daten
- ✅ Automatisierte UI-Tests

### UI Endpoints

```
GET /             # Weiterleitung zum Dashboard
GET /dashboard/   # Dashboard-Übersicht
```

---

## ✅ PDF-Unterlagen - IMPLEMENTIERT

### Features
- ✅ PDF-Upload pro Modul
- ✅ Datei-Metadaten mit Titel, Originaldateiname und Seitenanzahl
- ✅ Automatische Textextraktion mit `pypdf`
- ✅ Suche innerhalb extrahierter PDF-Inhalte
- ✅ Suchergebnisse mit Modul, Titel und Treffer-Snippet
- ✅ Filter nach Modul und Metadaten-Suche
- ✅ Nutzer sehen und bearbeiten nur ihre eigenen Unterlagen
- ✅ REST API Endpoints
- ✅ Server-rendered UI-Seiten für PDF-Unterlagen
- ✅ PDF-Upload, Bearbeiten und Löschen über die Weboberfläche
- ✅ Eigene PDF-Suchseite für extrahierte Inhalte
- ✅ Sidebar-Navigation führt auf echte PDF- und Suchseiten statt API-Platzhalter
- ✅ Django Admin Integration
- ✅ Automatisierte Tests mit kleiner Beispiel-PDF

### API Endpoints

```
GET    /api/materials/              # Eigene PDF-Unterlagen anzeigen
POST   /api/materials/              # PDF-Unterlage hochladen
GET    /api/materials/<id>/         # Einzelne PDF-Unterlage anzeigen
PATCH  /api/materials/<id>/         # PDF-Unterlage bearbeiten/ersetzen
DELETE /api/materials/<id>/         # PDF-Unterlage löschen
GET    /api/materials/search/?q=sql # PDF-Inhalte durchsuchen
```

### UI Endpoints

```
GET  /materials/              # PDF-Unterlagen anzeigen
GET  /materials/new/          # PDF-Unterlage hochladen
GET  /materials/<id>/edit/    # PDF-Unterlage bearbeiten
POST /materials/<id>/delete/  # PDF-Unterlage löschen
GET  /search/                 # PDF-Inhalte durchsuchen
```

### Filter & Suche

```
GET /api/materials/?module=<module_id>
GET /api/materials/?search=script
GET /api/materials/?ordering=-created_at
GET /api/materials/search/?q=relational%20algebra
GET /api/materials/search/?q=sql&module=<module_id>
```

---

## ✅ Qualität, Stabilisierung & UI-Vorbereitung - IMPLEMENTIERT

### Features
- ✅ Öffentlicher Health Check für lokale Entwicklung, Deployment und spätere UI-Startchecks
- ✅ API-Info-Endpunkt mit den wichtigsten Ressourcen für Frontend-Integration
- ✅ Gemeinsame Validierung für Datumsfilter, numerische IDs, Auswahlwerte und Sortierung
- ✅ Ungültige Query-Parameter liefern kontrollierte `400 Bad Request` Antworten
- ✅ `SECRET_KEY`, `DEBUG` und `ALLOWED_HOSTS` können über Umgebungsvariablen gesetzt werden
- ✅ Zusätzliche Tests für API-Stabilität und Fehlerfälle

### API Endpoints

```
GET /api/          # API-Info und wichtige Ressourcen
GET /api/health/   # Health Check
```

### Validierte Query-Parameter

```
date_before=YYYY-MM-DD
date_after=YYYY-MM-DD
module=<numeric_id>
ordering=<supported_field>
status=<supported_value>
```

---

## ✅ Qualitätssicherung

### Features
- ✅ 188 automatisierte Tests
- ✅ REST API Endpoints
- ✅ Model-Tests
- ✅ API-Tests
- ✅ Query-Param-Validierung
- ✅ Health/API-Info-Tests
- ✅ Dashboard-UI-Tests
- ✅ Login-/Registrierungs-UI-Tests
- ✅ Module-/Vorlesungen-UI-Tests
- ✅ Aufgaben-UI-Tests
- ✅ Abgaben-/Prüfungen-UI-Tests
- ✅ Lernplan-UI-Tests
- ✅ Fortschritt-/PDF-/Such-UI-Tests

---

## 📊 Projektstruktur

```
Study-Management-Tool/
├── config/                      # Django Projekt-Konfiguration
├── apps/
│   ├── ui/                      # Dashboard und serverseitige UI-Seiten
│   │   ├── forms.py
│   │   ├── course_views.py
│   │   ├── deadline_views.py
│   │   ├── material_views.py
│   │   ├── plan_views.py
│   │   ├── progress_views.py
│   │   ├── task_views.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── core/                    # API-Info, Health Check & Query-Helfer
│   │   ├── views.py
│   │   ├── query_params.py
│   │   └── urls.py
│   ├── accounts/                # Authentifizierung
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── urls.py
│   ├── courses/                 # Module & Vorlesungen
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── urls.py
│   ├── deadlines/               # Abgaben & Prüfungen
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── urls.py
│   ├── plans/                   # Lernpläne
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── urls.py
│   ├── overview/                # Fortschritt & Kalender
│   │   ├── services.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── materials/               # PDF-Unterlagen
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── services.py
│   │   └── urls.py
│   └── tasks/                   # Aufgabenmanagement
│       ├── models.py
│       ├── views.py
│       ├── serializers.py
│       └── urls.py
├── templates/                   # Django Templates
│   ├── base.html
│   └── ui/
│       ├── dashboard.html
│       ├── deadlines/
│       ├── lectures/
│       ├── materials/
│       ├── modules/
│       ├── plans/
│       ├── progress/
│       ├── search/
│       └── tasks/
├── tests/                       # 188 Tests
├── manage.py
├── pytest.ini
├── conftest.py
├── requirements.txt
└── Makefile
```

---

## 🧪 Testing

```bash
pytest                    # Alle Tests
pytest -v                 # Mit Ausgabe
pytest --cov=apps        # Mit Coverage
pytest -m authentication # Nur Auth-Tests
python manage.py check    # Django System Check
make check                # Alternative, falls make installiert ist
```

---

## Team-Arbeitsanweisung

Offene Prüfaufträge, Review-Regeln, Definition of Ready/Done und mögliche
Zusatzfunktionen stehen in:

`docs/TEAM_ARBEITSANWEISUNG.md`

---

**Status:** ✅ MVP funktionsfähig, Teamprüfung offen
