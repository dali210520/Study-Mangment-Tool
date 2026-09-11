"""
Server-rendered views for task management.
"""
from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.courses.models import StudyModule
from apps.tasks.models import Task

from .forms import TaskForm


STATUS_LABELS = {
    Task.Status.OPEN: 'Offen',
    Task.Status.IN_PROGRESS: 'In Bearbeitung',
    Task.Status.DONE: 'Erledigt',
}
PRIORITY_LABELS = {
    Task.Priority.LOW: 'Niedrig',
    Task.Priority.MEDIUM: 'Mittel',
    Task.Priority.HIGH: 'Hoch',
}
DUE_OPTIONS = (
    ('', 'Alle Fälligkeiten'),
    ('today', 'Heute'),
    ('overdue', 'Überfällig'),
    ('upcoming', 'Anstehend'),
    ('next_7_days', 'Nächste 7 Tage'),
)


class TaskListView(LoginRequiredMixin, ListView):
    """Show and filter tasks owned by the authenticated user."""

    template_name = 'ui/tasks/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        queryset = Task.objects.filter(user=self.request.user).select_related('module')
        query = self.request.GET.get('q', '').strip()
        status = self.request.GET.get('status', '').strip()
        priority = self.request.GET.get('priority', '').strip()
        module_id = self.request.GET.get('module', '').strip()
        due = self.request.GET.get('due', '').strip()
        today = timezone.localdate()

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(module__name__icontains=query)
            )
        if status in Task.Status.values:
            queryset = queryset.filter(status=status)
        if priority in Task.Priority.values:
            queryset = queryset.filter(priority=priority)
        if module_id.isdigit():
            queryset = queryset.filter(module_id=module_id, module__user=self.request.user)
        if due == 'today':
            queryset = queryset.filter(due_date=today)
        elif due == 'overdue':
            queryset = queryset.filter(due_date__lt=today).exclude(status=Task.Status.DONE)
        elif due == 'upcoming':
            queryset = queryset.filter(due_date__gte=today).exclude(status=Task.Status.DONE)
        elif due == 'next_7_days':
            queryset = queryset.filter(due_date__gte=today, due_date__lte=today + timedelta(days=7))

        return queryset.order_by('status', 'due_date', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        base_tasks = Task.objects.filter(user=self.request.user)
        today = timezone.localdate()
        for task in context['tasks']:
            task.status_label = STATUS_LABELS.get(task.status, task.get_status_display())
            task.priority_label = PRIORITY_LABELS.get(task.priority, task.get_priority_display())
            task.is_overdue = (
                task.due_date is not None
                and task.due_date < today
                and task.status != Task.Status.DONE
            )

        context.update(
            {
                'active_nav': 'tasks',
                'query': self.request.GET.get('q', '').strip(),
                'selected_status': self.request.GET.get('status', '').strip(),
                'selected_priority': self.request.GET.get('priority', '').strip(),
                'selected_module': self.request.GET.get('module', '').strip(),
                'selected_due': self.request.GET.get('due', '').strip(),
                'modules': StudyModule.objects.filter(user=self.request.user).order_by('name'),
                'status_options': [(value, STATUS_LABELS[value]) for value, _label in Task.Status.choices],
                'priority_options': [
                    (value, PRIORITY_LABELS[value]) for value, _label in Task.Priority.choices
                ],
                'status_labels': STATUS_LABELS,
                'priority_labels': PRIORITY_LABELS,
                'due_options': DUE_OPTIONS,
                'today': today,
                'task_total': base_tasks.count(),
                'open_count': base_tasks.filter(status=Task.Status.OPEN).count(),
                'in_progress_count': base_tasks.filter(status=Task.Status.IN_PROGRESS).count(),
                'done_count': base_tasks.filter(status=Task.Status.DONE).count(),
                'overdue_count': base_tasks.filter(due_date__lt=today)
                .exclude(status=Task.Status.DONE)
                .count(),
            }
        )
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    """Create a task for the authenticated user."""

    template_name = 'ui/tasks/task_form.html'
    form_class = TaskForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        date_param = self.request.GET.get('date')
        time_param = self.request.GET.get('time')
        if date_param:
            initial['due_date'] = date_param
        if time_param:
            initial['start_time'] = time_param
        return initial

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('ui-task-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'active_nav': 'tasks',
                'page_title': 'Aufgabe erstellen',
                'submit_label': 'Aufgabe speichern',
            }
        )
        return context


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    """Update one owned task."""

    template_name = 'ui/tasks/task_form.html'
    form_class = TaskForm
    context_object_name = 'task'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).select_related('module')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse('ui-task-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'active_nav': 'tasks',
                'page_title': 'Aufgabe bearbeiten',
                'submit_label': 'Aenderungen speichern',
            }
        )
        return context


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    """Delete one owned task."""

    template_name = 'ui/tasks/task_confirm_delete.html'
    context_object_name = 'task'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).select_related('module')

    def get_success_url(self):
        return reverse('ui-task-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_nav'] = 'tasks'
        return context


class TaskStatusUpdateView(LoginRequiredMixin, View):
    """Update the status of one owned task from the list view."""

    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk, user=request.user)
        status = request.POST.get('status')
        if status in Task.Status.values:
            was_done = (task.status == Task.Status.DONE)
            task.status = status
            task.save(update_fields=['status', 'completed_at', 'updated_at'])
            if status == Task.Status.DONE and not was_done:
                from django.contrib import messages
                import random
                MOTIVATIONS = [
                    "🎉 Super gemacht! '{title}' ist erledigt!",
                    "🔥 Stark! Wieder eine Aufgabe weniger: '{title}'",
                    "✅ Weiter so! Du hast '{title}' abgeschlossen!",
                    "🚀 Klasse! '{title}' abgehakt!"
                ]
                msg = random.choice(MOTIVATIONS).format(title=task.title)
                messages.success(request, msg)
        return redirect('ui-task-list')
