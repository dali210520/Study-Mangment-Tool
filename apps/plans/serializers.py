"""
Serializers for study plans.
"""
from rest_framework import serializers

from apps.courses.models import StudyModule
from apps.deadlines.models import Deadline

from .models import StudyPlanEntry


class StudyPlanEntrySerializer(serializers.ModelSerializer):
    """API representation for a study plan entry."""

    module = serializers.PrimaryKeyRelatedField(
        queryset=StudyModule.objects.none(),
        required=False,
        allow_null=True,
    )
    deadline = serializers.PrimaryKeyRelatedField(
        queryset=Deadline.objects.none(),
        required=False,
        allow_null=True,
    )
    module_name = serializers.CharField(source='module.name', read_only=True)
    deadline_title = serializers.CharField(source='deadline.title', read_only=True)

    class Meta:
        model = StudyPlanEntry
        fields = (
            'id',
            'module',
            'module_name',
            'deadline',
            'deadline_title',
            'topic',
            'planned_date',
            'duration_minutes',
            'status',
            'notes',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'module_name',
            'deadline_title',
            'created_at',
            'updated_at',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            self.fields['module'].queryset = StudyModule.objects.filter(user=request.user)
            self.fields['deadline'].queryset = Deadline.objects.filter(user=request.user)

    def validate_duration_minutes(self, value):
        """Keep study sessions useful and easy to reason about."""
        if value == 0:
            raise serializers.ValidationError('Duration must be greater than zero.')
        return value

    def validate(self, attrs):
        """Prevent linking somebody else's module or deadline."""
        request = self.context.get('request')
        module = attrs.get('module')
        deadline = attrs.get('deadline')

        if module and request and module.user_id != request.user.id:
            raise serializers.ValidationError({
                'module': 'Module must belong to the authenticated user.'
            })
        if deadline and request and deadline.user_id != request.user.id:
            raise serializers.ValidationError({
                'deadline': 'Deadline must belong to the authenticated user.'
            })
        return attrs
