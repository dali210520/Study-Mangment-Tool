"""
API views for uploaded study materials.
"""
from django.db.models import Q
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.query_params import apply_ordering, get_int_param, get_ordering_param

from .models import StudyMaterial
from .serializers import StudyMaterialSerializer


class StudyMaterialListCreateView(generics.ListCreateAPIView):
    """List and upload PDF materials for the authenticated user."""

    serializer_class = StudyMaterialSerializer
    ordering_fields = {
        'created_at': 'created_at',
        'title': 'title',
    }

    def get_queryset(self):
        queryset = StudyMaterial.objects.filter(user=self.request.user).select_related('module')
        query_params = self.request.query_params

        module_id = get_int_param(query_params, 'module')
        search = query_params.get('search')
        ordering = get_ordering_param(query_params, self.ordering_fields)

        if module_id:
            queryset = queryset.filter(module_id=module_id)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(original_filename__icontains=search)
                | Q(module__name__icontains=search)
            )

        return apply_ordering(queryset, ordering, self.ordering_fields)


class StudyMaterialDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Read, update or delete one uploaded PDF material."""

    serializer_class = StudyMaterialSerializer

    def get_queryset(self):
        return StudyMaterial.objects.filter(user=self.request.user).select_related('module')


class StudyMaterialSearchView(APIView):
    """Search inside extracted PDF text for the authenticated user."""

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        module_id = get_int_param(request.query_params, 'module')

        if not query:
            return Response([])

        queryset = StudyMaterial.objects.filter(
            Q(title__icontains=query)
            | Q(original_filename__icontains=query)
            | Q(module__name__icontains=query)
            | Q(extracted_text__icontains=query),
            user=request.user,
        ).select_related('module')

        if module_id:
            queryset = queryset.filter(module_id=module_id)

        results = [
            {
                'id': material.id,
                'title': material.title,
                'module': material.module_id,
                'module_name': material.module.name,
                'page_count': material.page_count,
                'snippet': self._build_snippet(material.extracted_text, query),
            }
            for material in queryset
        ]
        return Response(results)

    def _build_snippet(self, text, query):
        lower_text = text.lower()
        lower_query = query.lower()
        index = lower_text.find(lower_query)

        if index == -1:
            return text[:160]

        start = max(index - 60, 0)
        end = min(index + len(query) + 60, len(text))
        return text[start:end].strip()
