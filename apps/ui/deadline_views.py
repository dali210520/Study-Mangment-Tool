"""
Server-rendered views for assignments, exams and other deadlines.
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
from apps.deadlines.models import Deadline

from .forms import DeadlineForm


TYPE_LABELS = {
    Deadline.DeadlineType.ASSIGNMENT: 'Abgabe',
    Deadline.DeadlineType.EXAM: 'Prüfung',
    Deadline.DeadlineType.PRESENTATION: 'Präsentation',
    Deadline.DeadlineType.PROJECT: 'Projekt',
    Deadline.DeadlineType.OTHER: 'Sonstiges',
}
STATUS_LABELS = {
    Deadline.Status.UPCOMING: 'Anstehend',
    Deadline.Status.COMPLETED: 'Erledigt',
    Deadline.Status.CANCELLED: 'Abgebrochen',
}
DATE_OPTIONS = (
    ('', 'Alle Termine'),
    ('today', 'Heute'),
    ('overdue', 'Überfällig'),
    ('upcoming', 'Anstehend'),
    ('next_7_days', 'Nächste 7 Tage'),
)


class DeadlineListView(LoginRequiredMixin, ListView):
    """Show and filter deadlines owned by the authenticated user."""

    template_name = 'ui/deadlines/deadline_list.html'
    context_object_name = 'deadlines'

    def get_queryset(self):
        queryset = Deadline.objects.filter(user=self.request.user).select_related('module')
        query = self.request.GET.get('q', '').strip()
        deadline_type = self.request.GET.get('type', '').strip()
        status = self.request.GET.get('status', '').strip()
        module_id = self.request.GET.get('module', '').strip()
        date = self.request.GET.get('date', '').strip()
        today = timezone.localdate()

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(notes__icontains=query)
                | Q(module__name__icontains=query)
            )
        if deadline_type in Deadline.DeadlineType.values:
            queryset = queryset.filter(deadline_type=deadline_type)
        if status in Deadline.Status.values:
            queryset = queryset.filter(status=status)
        if module_id.isdigit():
            queryset = queryset.filter(module_id=module_id, module__user=self.request.user)
        if date == 'today':
            queryset = queryset.filter(date=today)
        elif date == 'overdue':
            queryset = queryset.filter(date__lt=today, status=Deadline.Status.UPCOMING)
        elif date == 'upcoming':
            queryset = queryset.filter(date__gte=today)
        elif date == 'next_7_days':
            queryset = queryset.filter(date__gte=today, date__lte=today + timedelta(days=7))

        return queryset.order_by('date', 'title')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        base_deadlines = Deadline.objects.filter(user=self.request.user)
        today = timezone.localdate()
        for deadline in context['deadlines']:
            deadline.type_label = TYPE_LABELS.get(
                deadline.deadline_type,
                deadline.get_deadline_type_display(),
            )
            deadline.status_label = STATUS_LABELS.get(deadline.status, deadline.get_status_display())
            deadline.is_overdue = (
                deadline.date < today and deadline.status == Deadline.Status.UPCOMING
            )

        context.update(
            {
                'active_nav': 'deadlines',
                'query': self.request.GET.get('q', '').strip(),
                'selected_type': self.request.GET.get('type', '').strip(),
                'selected_status': self.request.GET.get('status', '').strip(),
                'selected_module': self.request.GET.get('module', '').strip(),
                'selected_date': self.request.GET.get('date', '').strip(),
                'modules': StudyModule.objects.filter(user=self.request.user).order_by('name'),
                'type_options': [
                    (value, TYPE_LABELS[value]) for value, _label in Deadline.DeadlineType.choices
                ],
                'status_options': [
                    (value, STATUS_LABELS[value]) for value, _label in Deadline.Status.choices
                ],
                'date_options': DATE_OPTIONS,
                'deadline_total': base_deadlines.count(),
                'upcoming_count': base_deadlines.filter(status=Deadline.Status.UPCOMING).count(),
                'completed_count': base_deadlines.filter(status=Deadline.Status.COMPLETED).count(),
                'exam_count': base_deadlines.filter(deadline_type=Deadline.DeadlineType.EXAM).count(),
                'overdue_count': base_deadlines.filter(
                    date__lt=today,
                    status=Deadline.Status.UPCOMING,
                ).count(),
            }
        )
        return context


class DeadlineCreateView(LoginRequiredMixin, CreateView):
    """Create a deadline for the authenticated user."""

    template_name = 'ui/deadlines/deadline_form.html'
    form_class = DeadlineForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        date_param = self.request.GET.get('date')
        time_param = self.request.GET.get('time')
        if date_param:
            initial['date'] = date_param
        if time_param:
            initial['start_time'] = time_param
        return initial

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('ui-deadline-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'active_nav': 'deadlines',
                'page_title': 'Abgabe oder Prüfung erstellen',
                'submit_label': 'Termin speichern',
            }
        )
        return context


class DeadlineUpdateView(LoginRequiredMixin, UpdateView):
    """Update one owned deadline."""

    template_name = 'ui/deadlines/deadline_form.html'
    form_class = DeadlineForm
    context_object_name = 'deadline'

    def get_queryset(self):
        return Deadline.objects.filter(user=self.request.user).select_related('module')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse('ui-deadline-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'active_nav': 'deadlines',
                'page_title': 'Abgabe oder Prüfung bearbeiten',
                'submit_label': 'Aenderungen speichern',
            }
        )
        return context


class DeadlineDeleteView(LoginRequiredMixin, DeleteView):
    """Delete one owned deadline."""

    template_name = 'ui/deadlines/deadline_confirm_delete.html'
    context_object_name = 'deadline'

    def get_queryset(self):
        return Deadline.objects.filter(user=self.request.user).select_related('module')

    def get_success_url(self):
        return reverse('ui-deadline-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_nav'] = 'deadlines'
        return context


class DeadlineStatusUpdateView(LoginRequiredMixin, View):
    """Update the status of one owned deadline from the list view."""

    def post(self, request, pk):
        deadline = get_object_or_404(Deadline, pk=pk, user=request.user)
        status = request.POST.get('status')
        if status in Deadline.Status.values:
            was_completed = (deadline.status == Deadline.Status.COMPLETED)
            deadline.status = status
            deadline.save(update_fields=['status', 'updated_at'])
            if status == Deadline.Status.COMPLETED and not was_completed:
                from django.contrib import messages
                import random
                MOTIVATIONS = [
                    "🎉 Super gemacht! '{title}' ist erledigt!",
                    "🔥 Stark! Wieder eine Aufgabe weniger: '{title}'",
                    "✅ Weiter so! Du hast '{title}' abgeschlossen!",
                    "🚀 Klasse! '{title}' abgehakt!"
                ]
                msg = random.choice(MOTIVATIONS).format(title=deadline.title)
                messages.success(request, msg)
        return redirect('ui-deadline-list')
