"""
Serializers for study materials.
"""
from pathlib import Path

from rest_framework import serializers

from apps.courses.models import StudyModule

from .models import StudyMaterial
from .services import extract_pdf_text


class StudyMaterialSerializer(serializers.ModelSerializer):
    """API representation for an uploaded PDF material."""

    module = serializers.PrimaryKeyRelatedField(queryset=StudyModule.objects.none())
    module_name = serializers.CharField(source='module.name', read_only=True)
    file = serializers.FileField(write_only=True, required=False)
    file_url = serializers.FileField(source='file', read_only=True)

    class Meta:
        model = StudyMaterial
        fields = (
            'id',
            'module',
            'module_name',
            'title',
            'file',
            'file_url',
            'original_filename',
            'page_count',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'module_name',
            'file_url',
            'original_filename',
            'page_count',
            'created_at',
            'updated_at',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            self.fields['module'].queryset = StudyModule.objects.filter(user=request.user)

    def validate_file(self, value):
        """Validate PDF extension and extractability early."""
        if Path(value.name).suffix.lower() != '.pdf':
            raise serializers.ValidationError('Only PDF files are supported.')

        try:
            extract_pdf_text(value)
        except Exception as exc:
            raise serializers.ValidationError('Uploaded file is not a readable PDF.') from exc

        return value

    def validate(self, attrs):
        """Prevent assigning a material to somebody else's module."""
        request = self.context.get('request')
        module = attrs.get('module')
        uploaded_file = attrs.get('file')
        if self.instance is None and uploaded_file is None:
            raise serializers.ValidationError({
                'file': 'A PDF file is required.'
            })
        if module and request and module.user_id != request.user.id:
            raise serializers.ValidationError({
                'module': 'Module must belong to the authenticated user.'
            })
        return attrs

    def create(self, validated_data):
        request = self.context['request']
        uploaded_file = validated_data['file']
        validated_data['user'] = request.user
        validated_data['original_filename'] = uploaded_file.name

        material = super().create(validated_data)
        self._extract_and_store_text(material)
        return material

    def update(self, instance, validated_data):
        uploaded_file = validated_data.get('file')
        if uploaded_file:
            validated_data['original_filename'] = uploaded_file.name

        material = super().update(instance, validated_data)
        if uploaded_file:
            self._extract_and_store_text(material)
        return material

    def _extract_and_store_text(self, material):
        with material.file.open('rb') as file_obj:
            extracted_text, page_count = extract_pdf_text(file_obj)

        material.extracted_text = extracted_text
        material.page_count = page_count
        material.save(update_fields=['extracted_text', 'page_count', 'updated_at'])


class StudyMaterialSearchResultSerializer(serializers.Serializer):
    """Search result for a PDF material text match."""

    id = serializers.IntegerField()
    title = serializers.CharField()
    module = serializers.IntegerField()
    module_name = serializers.CharField()
    page_count = serializers.IntegerField()
    snippet = serializers.CharField()
