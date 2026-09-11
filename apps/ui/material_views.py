"""
Server-rendered views for PDF study materials and material search.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from apps.courses.models import StudyModule
from apps.materials.models import StudyMaterial

from .forms import StudyMaterialForm


class StudyMaterialListView(LoginRequiredMixin, ListView):
    """Show and filter uploaded PDF materials owned by the authenticated user."""

    template_name = 'ui/materials/material_list.html'
    context_object_name = 'materials'

    def get_queryset(self):
        queryset = StudyMaterial.objects.filter(user=self.request.user).select_related('module')
        query = self.request.GET.get('q', '').strip()
        module_id = self.request.GET.get('module', '').strip()

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(original_filename__icontains=query)
                | Q(module__name__icontains=query)
            )
        if module_id.isdigit():
            queryset = queryset.filter(module_id=module_id, module__user=self.request.user)

        return queryset.order_by('title')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        base_materials = StudyMaterial.objects.filter(user=self.request.user)
        context.update(
            {
                'active_nav': 'materials',
                'query': self.request.GET.get('q', '').strip(),
                'selected_module': self.request.GET.get('module', '').strip(),
                'modules': StudyModule.objects.filter(user=self.request.user).order_by('name'),
                'material_total': base_materials.count(),
                'page_total': sum(material.page_count for material in base_materials),
            }
        )
        return context


class StudyMaterialCreateView(LoginRequiredMixin, CreateView):
    """Upload a PDF material for the authenticated user."""

    template_name = 'ui/materials/material_form.html'
    form_class = StudyMaterialForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self._apply_uploaded_file_metadata(form)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('ui-material-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'active_nav': 'materials',
                'page_title': 'PDF-Unterlage hochladen',
                'submit_label': 'Unterlage speichern',
            }
        )
        return context

    def _apply_uploaded_file_metadata(self, form):
        uploaded_file = form.cleaned_data.get('file')
        if uploaded_file and not getattr(uploaded_file, '_committed', False):
            self.object.original_filename = uploaded_file.name
            self.object.extracted_text = form.extracted_text or ''
            self.object.page_count = form.page_count or 0


class StudyMaterialUpdateView(LoginRequiredMixin, UpdateView):
    """Update one owned PDF material."""

    template_name = 'ui/materials/material_form.html'
    form_class = StudyMaterialForm
    context_object_name = 'material'

    def get_queryset(self):
        return StudyMaterial.objects.filter(user=self.request.user).select_related('module')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self._apply_uploaded_file_metadata(form)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('ui-material-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'active_nav': 'materials',
                'page_title': 'PDF-Unterlage bearbeiten',
                'submit_label': 'Aenderungen speichern',
            }
        )
        return context

    def _apply_uploaded_file_metadata(self, form):
        uploaded_file = form.cleaned_data.get('file')
        if uploaded_file and not getattr(uploaded_file, '_committed', False):
            self.object.original_filename = uploaded_file.name
            self.object.extracted_text = form.extracted_text or ''
            self.object.page_count = form.page_count or 0


class StudyMaterialDeleteView(LoginRequiredMixin, DeleteView):
    """Delete one owned PDF material."""

    template_name = 'ui/materials/material_confirm_delete.html'
    context_object_name = 'material'

    def get_queryset(self):
        return StudyMaterial.objects.filter(user=self.request.user).select_related('module')

    def get_success_url(self):
        return reverse('ui-material-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_nav'] = 'materials'
        return context


class MaterialSearchView(LoginRequiredMixin, TemplateView):
    """Search inside extracted PDF text for the authenticated user."""

    template_name = 'ui/search/search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        module_id = self.request.GET.get('module', '').strip()
        results = []

        if query:
            queryset = StudyMaterial.objects.filter(
                Q(title__icontains=query)
                | Q(original_filename__icontains=query)
                | Q(module__name__icontains=query)
                | Q(extracted_text__icontains=query),
                user=self.request.user,
            ).select_related('module')
            if module_id.isdigit():
                queryset = queryset.filter(module_id=module_id, module__user=self.request.user)
            results = [
                {
                    'material': material,
                    'snippet': self._build_snippet(material.extracted_text, query),
                }
                for material in queryset.order_by('title')
            ]

        context.update(
            {
                'active_nav': 'search',
                'query': query,
                'selected_module': module_id,
                'modules': StudyModule.objects.filter(user=self.request.user).order_by('name'),
                'results': results,
                'searched': bool(query),
            }
        )
        return context

    def _build_snippet(self, text, query):
        lower_text = text.lower()
        lower_query = query.lower()
        index = lower_text.find(lower_query)
        if index == -1:
            return text[:160]

        start = max(index - 60, 0)
        end = min(index + len(query) + 60, len(text))
        return text[start:end].strip()
