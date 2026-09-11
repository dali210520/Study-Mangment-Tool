"""
Server-rendered views for study plan entries.
"""
from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.courses.models import StudyModule
from apps.deadlines.models import Deadline
from apps.plans.models import StudyPlanEntry

from .forms import StudyPlanEntryForm


STATUS_LABELS = {
    StudyPlanEntry.Status.PLANNED: 'Geplant',
    StudyPlanEntry.Status.IN_PROGRESS: 'In Bearbeitung',
    StudyPlanEntry.Status.DONE: 'Erledigt',
    StudyPlanEntry.Status.SKIPPED: 'Übersprungen',
}
DATE_OPTIONS = (
    ('', 'Alle Termine'),
    ('today', 'Heute'),
    ('past', 'Vergangen'),
    ('upcoming', 'Anstehend'),
    ('next_7_days', 'Nächste 7 Tage'),
)


class StudyPlanEntryListView(LoginRequiredMixin, ListView):
    """Show and filter study plan entries owned by the authenticated user."""

    template_name = 'ui/plans/plan_list.html'
    context_object_name = 'entries'

    def get_queryset(self):
        queryset = StudyPlanEntry.objects.filter(user=self.request.user).select_related(
            'module',
            'deadline',
        )
        query = self.request.GET.get('q', '').strip()
        status = self.request.GET.get('status', '').strip()
        module_id = self.request.GET.get('module', '').strip()
        deadline_id = self.request.GET.get('deadline', '').strip()
        date = self.request.GET.get('date', '').strip()
        today = timezone.localdate()

        if query:
            queryset = queryset.filter(
                Q(topic__icontains=query)
                | Q(notes__icontains=query)
                | Q(module__name__icontains=query)
                | Q(deadline__title__icontains=query)
            )
        if status in StudyPlanEntry.Status.values:
            queryset = queryset.filter(status=status)
        if module_id.isdigit():
            queryset = queryset.filter(module_id=module_id, module__user=self.request.user)
        if deadline_id.isdigit():
            queryset = queryset.filter(deadline_id=deadline_id, deadline__user=self.request.user)
        if date == 'today':
            queryset = queryset.filter(planned_date=today)
        elif date == 'past':
            queryset = queryset.filter(planned_date__lt=today)
        elif date == 'upcoming':
            queryset = queryset.filter(planned_date__gte=today)
        elif date == 'next_7_days':
            queryset = queryset.filter(
                planned_date__gte=today,
                planned_date__lte=today + timedelta(days=7),
            )

        return queryset.order_by('planned_date', 'topic')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        base_entries = StudyPlanEntry.objects.filter(user=self.request.user)
        today = timezone.localdate()
        for entry in context['entries']:
            entry.status_label = STATUS_LABELS.get(entry.status, entry.get_status_display())
            entry.is_past_due = (
                entry.planned_date < today
                and entry.status not in {StudyPlanEntry.Status.DONE, StudyPlanEntry.Status.SKIPPED}
            )

        context.update(
            {
                'active_nav': 'plans',
                'query': self.request.GET.get('q', '').strip(),
                'selected_status': self.request.GET.get('status', '').strip(),
                'selected_module': self.request.GET.get('module', '').strip(),
                'selected_deadline': self.request.GET.get('deadline', '').strip(),
                'selected_date': self.request.GET.get('date', '').strip(),
                'modules': StudyModule.objects.filter(user=self.request.user).order_by('name'),
                'deadlines': Deadline.objects.filter(user=self.request.user).order_by(
                    'date',
                    'title',
                ),
                'status_options': [
                    (value, STATUS_LABELS[value]) for value, _label in StudyPlanEntry.Status.choices
                ],
                'date_options': DATE_OPTIONS,
                'entry_total': base_entries.count(),
                'planned_count': base_entries.filter(status=StudyPlanEntry.Status.PLANNED).count(),
                'in_progress_count': base_entries.filter(
                    status=StudyPlanEntry.Status.IN_PROGRESS,
                ).count(),
                'done_count': base_entries.filter(status=StudyPlanEntry.Status.DONE).count(),
                'planned_minutes': base_entries.exclude(
                    status=StudyPlanEntry.Status.SKIPPED,
                ).aggregate(total=Sum('duration_minutes'))['total']
                or 0,
            }
        )
        return context


class StudyPlanEntryCreateView(LoginRequiredMixin, CreateView):
    """Create a study plan entry for the authenticated user."""

    template_name = 'ui/plans/plan_form.html'
    form_class = StudyPlanEntryForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        date_param = self.request.GET.get('date')
        if date_param:
            initial['planned_date'] = date_param
        return initial

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('ui-plan-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'active_nav': 'plans',
                'page_title': 'Lernplan erstellen',
                'submit_label': 'Lernplan speichern',
            }
        )
        return context


class StudyPlanEntryUpdateView(LoginRequiredMixin, UpdateView):
    """Update one owned study plan entry."""

    template_name = 'ui/plans/plan_form.html'
    form_class = StudyPlanEntryForm
    context_object_name = 'entry'

    def get_queryset(self):
        return StudyPlanEntry.objects.filter(user=self.request.user).select_related(
            'module',
            'deadline',
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse('ui-plan-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'active_nav': 'plans',
                'page_title': 'Lernplan bearbeiten',
                'submit_label': 'Aenderungen speichern',
            }
        )
        return context


class StudyPlanEntryDeleteView(LoginRequiredMixin, DeleteView):
    """Delete one owned study plan entry."""

    template_name = 'ui/plans/plan_confirm_delete.html'
    context_object_name = 'entry'

    def get_queryset(self):
        return StudyPlanEntry.objects.filter(user=self.request.user).select_related(
            'module',
            'deadline',
        )

    def get_success_url(self):
        return reverse('ui-plan-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_nav'] = 'plans'
        return context


class StudyPlanEntryStatusUpdateView(LoginRequiredMixin, View):
    """Update the status of one owned study plan entry from the list view."""

    def post(self, request, pk):
        entry = get_object_or_404(StudyPlanEntry, pk=pk, user=request.user)
        status = request.POST.get('status')
        if status in StudyPlanEntry.Status.values:
            was_done = (entry.status == StudyPlanEntry.Status.DONE)
            entry.status = status
            entry.save(update_fields=['status', 'updated_at'])
            if status == StudyPlanEntry.Status.DONE and not was_done:
                from django.contrib import messages
                import random
                MOTIVATIONS = [
                    "🎉 Super gemacht! '{title}' ist erledigt!",
                    "🔥 Stark! Wieder eine Aufgabe weniger: '{title}'",
                    "✅ Weiter so! Du hast '{title}' abgeschlossen!",
                    "🚀 Klasse! '{title}' abgehakt!"
                ]
                msg = random.choice(MOTIVATIONS).format(title=entry.topic)
                messages.success(request, msg)
        return redirect('ui-plan-list')
