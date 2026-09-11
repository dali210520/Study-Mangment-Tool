"""
Serializers for study modules and lectures.
"""
from rest_framework import serializers

from .models import Lecture, StudyModule


class StudyModuleSerializer(serializers.ModelSerializer):
    """API representation for a study module."""

    lecture_count = serializers.IntegerField(
        source='lectures.count',
        read_only=True,
    )

    class Meta:
        model = StudyModule
        fields = (
            'id',
            'name',
            'semester',
            'lecturer',
            'description',
            'lecture_count',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'lecture_count', 'created_at', 'updated_at')


class LectureSerializer(serializers.ModelSerializer):
    """API representation for a lecture."""

    module = serializers.PrimaryKeyRelatedField(read_only=True)
    module_name = serializers.CharField(source='module.name', read_only=True)

    class Meta:
        model = Lecture
        fields = (
            'id',
            'module',
            'module_name',
            'title',
            'date',
            'notes',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'module', 'module_name', 'created_at', 'updated_at')
