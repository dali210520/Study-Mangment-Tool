"""
Serializers for assignments and exams.
"""
from django.utils import timezone
from rest_framework import serializers

from apps.courses.models import StudyModule

from .models import Deadline


class DeadlineSerializer(serializers.ModelSerializer):
    """API representation for an academic deadline."""

    module = serializers.PrimaryKeyRelatedField(
        queryset=StudyModule.objects.none(),
        required=False,
        allow_null=True,
    )
    module_name = serializers.CharField(source='module.name', read_only=True)
    is_past_due = serializers.SerializerMethodField()

    class Meta:
        model = Deadline
        fields = (
            'id',
            'module',
            'module_name',
            'title',
            'deadline_type',
            'date',
            'notes',
            'status',
            'is_past_due',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'module_name', 'is_past_due', 'created_at', 'updated_at')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            self.fields['module'].queryset = StudyModule.objects.filter(user=request.user)

    def get_is_past_due(self, obj):
        """Return whether the deadline date is before today."""
        return obj.date < timezone.localdate()

    def validate(self, attrs):
        """Prevent assigning deadlines to somebody else's module."""
        module = attrs.get('module')
        request = self.context.get('request')
        if module and request and module.user_id != request.user.id:
            raise serializers.ValidationError({
                'module': 'Module must belong to the authenticated user.'
            })
        return attrs
