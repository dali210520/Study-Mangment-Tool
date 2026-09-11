"""
Server-rendered views for modules and lectures.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.courses.models import Lecture, StudyModule

from .forms import GlobalLectureForm, LectureForm, StudyModuleForm


class ModuleListView(LoginRequiredMixin, ListView):
    """Show modules owned by the authenticated user."""

    template_name = 'ui/modules/module_list.html'
    context_object_name = 'modules'

    def get_queryset(self):
        queryset = StudyModule.objects.filter(user=self.request.user).annotate(
            lecture_total=Count('lectures'),
        )
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query)
                | Q(semester__icontains=query)
                | Q(lecturer__icontains=query)
                | Q(description__icontains=query)
            )
        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        modules = context['modules']
        context.update(
            {
                'active_nav': 'modules',
                'query': self.request.GET.get('q', '').strip(),
                'module_count': modules.count(),
                'lecture_count': Lecture.objects.filter(module__user=self.request.user).count(),
            }
        )
        return context


class ModuleDetailView(LoginRequiredMixin, DetailView):
    """Show one owned module and its lectures."""

    template_name = 'ui/modules/module_detail.html'
    context_object_name = 'module'

    def get_queryset(self):
        return StudyModule.objects.filter(user=self.request.user).prefetch_related('lectures')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        module = self.object
        context.update(
            {
                'active_nav': 'modules',
                'lectures': module.lectures.all(),
                'task_count': module.tasks.count(),
                'deadline_count': module.deadlines.count(),
                'material_count': module.study_materials.count(),
            }
        )
        return context


class ModuleCreateView(LoginRequiredMixin, CreateView):
    """Create a study module for the authenticated user."""

    template_name = 'ui/modules/module_form.html'
    form_class = StudyModuleForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('ui-module-detail', args=[self.object.id])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'active_nav': 'modules',
                'page_title': 'Modul erstellen',
                'submit_label': 'Modul speichern',
            }
        )
        return context


class ModuleUpdateView(LoginRequiredMixin, UpdateView):
    """Update one owned module."""

    template_name = 'ui/modules/module_form.html'
    form_class = StudyModuleForm
    context_object_name = 'module'

    def get_queryset(self):
        return StudyModule.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse('ui-module-detail', args=[self.object.id])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'active_nav': 'modules',
                'page_title': 'Modul bearbeiten',
                'submit_label': 'Aenderungen speichern',
            }
        )
        return context


class ModuleDeleteView(LoginRequiredMixin, DeleteView):
    """Delete one owned module."""

    template_name = 'ui/modules/module_confirm_delete.html'
    context_object_name = 'module'

    def get_queryset(self):
        return StudyModule.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse('ui-module-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_nav'] = 'modules'
        return context


class LectureListView(LoginRequiredMixin, ListView):
    """Show all lectures from owned modules."""

    template_name = 'ui/lectures/lecture_list.html'
    context_object_name = 'lectures'

    def get_queryset(self):
        queryset = Lecture.objects.filter(module__user=self.request.user).select_related('module')
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(notes__icontains=query)
                | Q(module__name__icontains=query)
            )
        return queryset.order_by('date', 'title')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'active_nav': 'lectures',
                'query': self.request.GET.get('q', '').strip(),
                'module_count': StudyModule.objects.filter(user=self.request.user).count(),
            }
        )
        return context


class GlobalLectureCreateView(LoginRequiredMixin, CreateView):
    """Create a lecture globally with module selection."""

    template_name = 'ui/lectures/lecture_form.html'
    form_class = GlobalLectureForm

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
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('ui-lecture-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'active_nav': 'lectures',
                'page_title': 'Vorlesung erstellen',
                'submit_label': 'Vorlesung speichern',
                'global_create': True,
            }
        )
        return context


class LectureCreateView(LoginRequiredMixin, CreateView):
    """Create a lecture inside one owned module."""

    template_name = 'ui/lectures/lecture_form.html'
    form_class = LectureForm

    def dispatch(self, request, *args, **kwargs):
        self.module = get_object_or_404(
            StudyModule,
            id=kwargs['module_id'],
            user=request.user,
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.module = self.module
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('ui-module-detail', args=[self.module.id])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'active_nav': 'lectures',
                'module': self.module,
                'page_title': 'Vorlesung erstellen',
                'submit_label': 'Vorlesung speichern',
            }
        )
        return context


class LectureUpdateView(LoginRequiredMixin, UpdateView):
    """Update a lecture from an owned module."""

    template_name = 'ui/lectures/lecture_form.html'
    form_class = LectureForm
    context_object_name = 'lecture'

    def get_queryset(self):
        return Lecture.objects.filter(module__user=self.request.user).select_related('module')

    def get_success_url(self):
        return reverse('ui-module-detail', args=[self.object.module_id])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'active_nav': 'lectures',
                'module': self.object.module,
                'page_title': 'Vorlesung bearbeiten',
                'submit_label': 'Aenderungen speichern',
            }
        )
        return context


class LectureDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a lecture from an owned module."""

    template_name = 'ui/lectures/lecture_confirm_delete.html'
    context_object_name = 'lecture'

    def get_queryset(self):
        return Lecture.objects.filter(module__user=self.request.user).select_related('module')

    def get_success_url(self):
        return reverse('ui-module-detail', args=[self.object.module_id])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'active_nav': 'lectures',
                'module': self.object.module,
            }
        )
        return context
