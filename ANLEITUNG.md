# Anleitung: Projekt lokal in der IDE starten

Diese Anleitung beschreibt, wie du das Study-Management-Tool lokal startest,
nachdem du `main` aktualisiert hast und auf deinem Arbeitsbranch weiterarbeiten
möchtest.

## 1. Voraussetzungen

Du brauchst lokal:

- Git
- Python 3.9 oder neuer
- PyCharm oder eine andere IDE
- Zugriff auf das GitHub-Repository

Optional, aber hilfreich:

- Ein Terminal direkt in der IDE
- Grundkenntnisse in Git: `fetch`, `pull`, `switch`, `status`

## 2. Repository aktualisieren und Branch wählen

Im Projektordner:

```powershell
git fetch origin
git switch main
git pull origin main
```

Danach auf den gewünschten Branch wechseln:

```powershell
git switch <branch-name>
git pull origin <branch-name>
```

Wenn der Branch nur auf GitHub existiert und lokal noch nicht angelegt ist:

```powershell
git switch -c <branch-name> origin/<branch-name>
```

Beispiel:

```powershell
git switch -c codex/mein-feature origin/codex/mein-feature
```

Prüfen, ob du auf dem richtigen Branch bist:

```powershell
git status
```

## 3. Projekt in PyCharm öffnen

1. PyCharm öffnen.
2. `File` > `Open` wählen.
3. Den Projektordner öffnen:

```text
C:\Users\marvi\PycharmProjects\Study-Management-Tool
```

4. Warten, bis PyCharm das Projekt indexiert hat.

## 4. Virtuelle Umgebung erstellen

Im Terminal der IDE:

```powershell
python -m venv .venv
```

Virtuelle Umgebung aktivieren:

```powershell
.\.venv\Scripts\Activate.ps1
```

Falls PowerShell die Aktivierung blockiert:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Wenn die Umgebung aktiv ist, steht vorne im Terminal normalerweise `(.venv)`.

## 5. Requirements installieren

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Falls du nicht sicher bist, ob die richtige Python-Umgebung aktiv ist:

```powershell
python --version
pip --version
```

## 6. PyCharm Interpreter setzen

In PyCharm:

1. `File` > `Settings` öffnen.
2. `Project` > `Python Interpreter` wählen.
3. Als Interpreter diese Datei auswählen:

```text
.venv\Scripts\python.exe
```

Danach erkennt PyCharm Django, pytest und die installierten Pakete sauber.

## 7. Datenbank vorbereiten

Die lokale SQLite-Datenbank wird nicht mit Git versioniert. Deshalb musst du sie
lokal erstellen bzw. aktualisieren:

```powershell
python manage.py migrate
```

Optional für den Django-Admin:

```powershell
python manage.py createsuperuser
```

Für die normale App brauchst du keinen Admin-Account. Du kannst dich über die
Registrierungsseite selbst als normaler Nutzer anlegen.

## 8. Projekt starten

Im Terminal:

```powershell
python manage.py runserver
```

Danach im Browser öffnen:

```text
http://127.0.0.1:8000/
```

Wichtige Seiten:

- `http://127.0.0.1:8000/register/` für Registrierung
- `http://127.0.0.1:8000/login/` für Login
- `http://127.0.0.1:8000/dashboard/` für das Dashboard
- `http://127.0.0.1:8000/admin/` für den Django-Admin

Wenn Port `8000` belegt ist:

```powershell
python manage.py runserver 8001
```

Dann öffnest du:

```text
http://127.0.0.1:8001/
```

## 9. Start über PyCharm Run Configuration

Alternativ kannst du in PyCharm eine Run Configuration anlegen:

1. Oben rechts auf die Run-Konfiguration klicken.
2. `Edit Configurations...` öffnen.
3. Neue Python-Konfiguration anlegen.
4. Werte setzen:

```text
Name: Django Server
Script path: C:\Users\marvi\PycharmProjects\Study-Management-Tool\manage.py
Parameters: runserver
Working directory: C:\Users\marvi\PycharmProjects\Study-Management-Tool
Environment variables: DJANGO_SETTINGS_MODULE=config.settings
Python interpreter: .venv\Scripts\python.exe
```

Danach kannst du das Projekt direkt über den grünen Run-Button starten.

## 10. Tests ausführen

Alle Tests:

```powershell
pytest
```

Ausführlicher:

```powershell
pytest -v
```

Nur Authentifizierung:

```powershell
pytest -m authentication
```

Nur eine einzelne Testdatei:

```powershell
pytest tests/test_dashboard_ui.py
```

Django-Systemcheck:

```powershell
python manage.py check
```

## 11. Optional: lokale Umgebungsvariablen

Für die lokale Entwicklung funktionieren Standardwerte. Falls du trotzdem eine
`.env` nutzen möchtest, kannst du im Projektordner eine Datei `.env` anlegen:

```text
SECRET_KEY=change-me-local
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

Die `.env` wird nicht committed.

## 12. Häufige Probleme

### ModuleNotFoundError

Meist ist die virtuelle Umgebung nicht aktiv oder die Requirements fehlen.

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### no such table

Die Datenbank wurde noch nicht migriert.

```powershell
python manage.py migrate
```

### Falscher Branch

Prüfen:

```powershell
git status
```

Branch wechseln:

```powershell
git switch <branch-name>
```

### Admin-Login funktioniert, aber normaler Login nicht

Der Django-Admin liegt unter `/admin/`. Die normale App nutzt:

```text
http://127.0.0.1:8000/login/
```

Neue normale Nutzer legst du hier an:

```text
http://127.0.0.1:8000/register/
```

### Port bereits belegt

Einfach einen anderen Port nutzen:

```powershell
python manage.py runserver 8001
```

## 13. Kurzfassung

```powershell
git fetch origin
git switch main
git pull origin main
git switch <branch-name>
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Dann öffnen:

```text
http://127.0.0.1:8000/
```
