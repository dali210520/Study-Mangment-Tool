"""
Serializers for task management.
"""
from rest_framework import serializers

from apps.courses.models import StudyModule

from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    """API representation for a student task."""

    module = serializers.PrimaryKeyRelatedField(
        queryset=StudyModule.objects.none(),
        required=False,
        allow_null=True,
    )
    module_name = serializers.CharField(source='module.name', read_only=True)

    class Meta:
        model = Task
        fields = (
            'id',
            'module',
            'module_name',
            'title',
            'description',
            'due_date',
            'priority',
            'status',
            'completed_at',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'module_name', 'completed_at', 'created_at', 'updated_at')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            self.fields['module'].queryset = StudyModule.objects.filter(user=request.user)

    def validate(self, attrs):
        """Prevent changing a task to a module owned by somebody else."""
        module = attrs.get('module')
        request = self.context.get('request')
        if module and request and module.user_id != request.user.id:
            raise serializers.ValidationError({
                'module': 'Module must belong to the authenticated user.'
            })
        return attrs
