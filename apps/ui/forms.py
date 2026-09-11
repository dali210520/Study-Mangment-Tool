"""
Forms for the server-rendered authentication UI.
"""
from pathlib import Path

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from apps.courses.models import Lecture, StudyModule
from apps.deadlines.models import Deadline
from apps.materials.models import StudyMaterial
from apps.materials.services import extract_pdf_text
from apps.plans.models import StudyPlanEntry
from apps.tasks.models import Task


User = get_user_model()


class RegistrationForm(forms.ModelForm):
    """Create a regular user account from the UI."""

    password = forms.CharField(
        label='Passwort',
        min_length=8,
        widget=forms.PasswordInput,
    )
    password_confirm = forms.CharField(
        label='Passwort wiederholen',
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        labels = {
            'username': 'Benutzername',
            'email': 'E-Mail',
            'first_name': 'Vorname',
            'last_name': 'Nachname',
        }

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError('Diese E-Mail wird bereits verwendet.')
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError('Dieser Benutzername wird bereits verwendet.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Die Passwörter stimmen nicht überein.')

        if password:
            try:
                validate_password(password)
            except ValidationError as error:
                self.add_error('password', error)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class StudyModuleForm(forms.ModelForm):
    """Create or update a study module from the UI."""

    class Meta:
        model = StudyModule
        fields = ('name', 'semester', 'lecturer', 'description')
        labels = {
            'name': 'Modulname',
            'semester': 'Semester',
            'lecturer': 'Dozent',
            'description': 'Beschreibung',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class LectureForm(forms.ModelForm):
    """Create or update a lecture from the UI."""

    class Meta:
        model = Lecture
        fields = ('title', 'date', 'start_time', 'end_time', 'notes')
        labels = {
            'title': 'Titel',
            'date': 'Datum',
            'start_time': 'Startzeit',
            'end_time': 'Endzeit',
            'notes': 'Notizen',
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }


class GlobalLectureForm(forms.ModelForm):
    """Create a lecture globally with module selection."""

    class Meta:
        model = Lecture
        fields = ('module', 'title', 'date', 'start_time', 'end_time', 'notes')
        labels = {
            'module': 'Modul',
            'title': 'Titel',
            'date': 'Datum',
            'start_time': 'Startzeit',
            'end_time': 'Endzeit',
            'notes': 'Notizen',
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['module'].empty_label = 'Bitte Modul wählen'
        if user is not None:
            self.fields['module'].queryset = StudyModule.objects.filter(user=user).order_by('name')

    def clean_module(self):
        module = self.cleaned_data.get('module')
        if module and self.user is not None and module.user_id != self.user.id:
            raise ValidationError('Dieses Modul gehört nicht zu deinem Konto.')
        return module


class TaskForm(forms.ModelForm):
    """Create or update a task from the UI."""

    status_labels = {
        Task.Status.OPEN: 'Offen',
        Task.Status.IN_PROGRESS: 'In Bearbeitung',
        Task.Status.DONE: 'Erledigt',
    }
    priority_labels = {
        Task.Priority.LOW: 'Niedrig',
        Task.Priority.MEDIUM: 'Mittel',
        Task.Priority.HIGH: 'Hoch',
    }

    class Meta:
        model = Task
        fields = ('module', 'title', 'description', 'due_date', 'start_time', 'end_time', 'priority', 'status')
        labels = {
            'module': 'Modul',
            'title': 'Aufgabe',
            'description': 'Beschreibung',
            'due_date': 'Fälligkeitsdatum',
            'start_time': 'Startzeit',
            'end_time': 'Endzeit',
            'priority': 'Priorität',
            'status': 'Status',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['module'].required = False
        self.fields['module'].empty_label = 'Kein Modul'
        self.fields['status'].choices = [
            (value, self.status_labels[value]) for value, _label in Task.Status.choices
        ]
        self.fields['priority'].choices = [
            (value, self.priority_labels[value]) for value, _label in Task.Priority.choices
        ]
        if user is not None:
            self.fields['module'].queryset = StudyModule.objects.filter(user=user).order_by('name')

    def clean_module(self):
        module = self.cleaned_data.get('module')
        if module and self.user is not None and module.user_id != self.user.id:
            raise ValidationError('Dieses Modul gehört nicht zu deinem Konto.')
        return module


class DeadlineForm(forms.ModelForm):
    """Create or update an academic deadline from the UI."""

    type_labels = {
        Deadline.DeadlineType.ASSIGNMENT: 'Abgabe',
        Deadline.DeadlineType.EXAM: 'Prüfung',
        Deadline.DeadlineType.PRESENTATION: 'Präsentation',
        Deadline.DeadlineType.PROJECT: 'Projekt',
        Deadline.DeadlineType.OTHER: 'Sonstiges',
    }
    status_labels = {
        Deadline.Status.UPCOMING: 'Anstehend',
        Deadline.Status.COMPLETED: 'Erledigt',
        Deadline.Status.CANCELLED: 'Abgebrochen',
    }

    class Meta:
        model = Deadline
        fields = ('module', 'title', 'deadline_type', 'date', 'start_time', 'end_time', 'notes', 'status')
        labels = {
            'module': 'Modul',
            'title': 'Titel',
            'deadline_type': 'Art',
            'date': 'Datum',
            'start_time': 'Startzeit',
            'end_time': 'Endzeit',
            'notes': 'Notizen',
            'status': 'Status',
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['module'].required = False
        self.fields['module'].empty_label = 'Kein Modul'
        self.fields['deadline_type'].choices = [
            (value, self.type_labels[value]) for value, _label in Deadline.DeadlineType.choices
        ]
        self.fields['status'].choices = [
            (value, self.status_labels[value]) for value, _label in Deadline.Status.choices
        ]
        if user is not None:
            self.fields['module'].queryset = StudyModule.objects.filter(user=user).order_by('name')

    def clean_module(self):
        module = self.cleaned_data.get('module')
        if module and self.user is not None and module.user_id != self.user.id:
            raise ValidationError('Dieses Modul gehört nicht zu deinem Konto.')
        return module


class StudyPlanEntryForm(forms.ModelForm):
    """Create or update a study plan entry from the UI."""

    status_labels = {
        StudyPlanEntry.Status.PLANNED: 'Geplant',
        StudyPlanEntry.Status.IN_PROGRESS: 'In Bearbeitung',
        StudyPlanEntry.Status.DONE: 'Erledigt',
        StudyPlanEntry.Status.SKIPPED: 'Übersprungen',
    }

    class Meta:
        model = StudyPlanEntry
        fields = (
            'module',
            'deadline',
            'topic',
            'planned_date',
            'duration_minutes',
            'status',
            'notes',
        )
        labels = {
            'module': 'Modul',
            'deadline': 'Abgabe oder Prüfung',
            'topic': 'Lernthema',
            'planned_date': 'Lerndatum',
            'duration_minutes': 'Dauer in Minuten',
            'status': 'Status',
            'notes': 'Notizen',
        }
        widgets = {
            'planned_date': forms.DateInput(attrs={'type': 'date'}),
            'duration_minutes': forms.NumberInput(attrs={'min': 1}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['module'].required = False
        self.fields['module'].empty_label = 'Kein Modul'
        self.fields['deadline'].required = False
        self.fields['deadline'].empty_label = 'Keine Abgabe oder Prüfung'
        self.fields['status'].choices = [
            (value, self.status_labels[value]) for value, _label in StudyPlanEntry.Status.choices
        ]
        if user is not None:
            self.fields['module'].queryset = StudyModule.objects.filter(user=user).order_by('name')
            self.fields['deadline'].queryset = Deadline.objects.filter(user=user).order_by(
                'date',
                'title',
            )

    def clean_duration_minutes(self):
        duration = self.cleaned_data.get('duration_minutes')
        if duration is not None and duration <= 0:
            raise ValidationError('Die Dauer muss größer als 0 Minuten sein.')
        return duration

    def clean_module(self):
        module = self.cleaned_data.get('module')
        if module and self.user is not None and module.user_id != self.user.id:
            raise ValidationError('Dieses Modul gehört nicht zu deinem Konto.')
        return module

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if deadline and self.user is not None and deadline.user_id != self.user.id:
            raise ValidationError('Dieser Termin gehört nicht zu deinem Konto.')
        return deadline


class StudyMaterialForm(forms.ModelForm):
    """Upload or update a PDF study material from the UI."""

    class Meta:
        model = StudyMaterial
        fields = ('module', 'title', 'file')
        labels = {
            'module': 'Modul',
            'title': 'Titel',
            'file': 'PDF-Datei',
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        self.extracted_text = None
        self.page_count = None
        super().__init__(*args, **kwargs)
        self.fields['file'].required = self.instance.pk is None
        if user is not None:
            self.fields['module'].queryset = StudyModule.objects.filter(user=user).order_by('name')

    def clean_module(self):
        module = self.cleaned_data.get('module')
        if module and self.user is not None and module.user_id != self.user.id:
            raise ValidationError('Dieses Modul gehört nicht zu deinem Konto.')
        return module

    def clean_file(self):
        uploaded_file = self.cleaned_data.get('file')
        if not uploaded_file:
            return uploaded_file
        if getattr(uploaded_file, '_committed', False):
            return uploaded_file

        if Path(uploaded_file.name).suffix.lower() != '.pdf':
            raise ValidationError('Nur PDF-Dateien werden unterstützt.')

        try:
            self.extracted_text, self.page_count = extract_pdf_text(uploaded_file)
        except Exception as error:
            raise ValidationError('Die PDF-Datei konnte nicht gelesen werden.') from error

        return uploaded_file
