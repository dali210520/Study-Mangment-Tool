"""
Tests for course-related models.
"""
import pytest

from apps.courses.models import Lecture, StudyModule


@pytest.mark.django_db
@pytest.mark.unit
class TestStudyModuleModel:
    """Test cases for the StudyModule model."""

    def test_module_str_with_semester(self, authenticated_user):
        module = StudyModule.objects.create(
            user=authenticated_user,
            name='Software Engineering',
            semester='WS 2026',
        )

        assert str(module) == 'Software Engineering (WS 2026)'

    def test_module_str_without_semester(self, authenticated_user):
        module = StudyModule.objects.create(
            user=authenticated_user,
            name='Mathematics',
        )

        assert str(module) == 'Mathematics'


@pytest.mark.django_db
@pytest.mark.unit
class TestLectureModel:
    """Test cases for the Lecture model."""

    def test_lecture_str(self, authenticated_user):
        module = StudyModule.objects.create(
            user=authenticated_user,
            name='Databases',
        )
        lecture = Lecture.objects.create(
            module=module,
            title='Normalization',
            date='2026-10-15',
        )

        assert str(lecture) == '2026-10-15 - Normalization'

    def test_deleting_module_deletes_lectures(self, authenticated_user):
        module = StudyModule.objects.create(
            user=authenticated_user,
            name='Algorithms',
        )
        lecture = Lecture.objects.create(
            module=module,
            title='Sorting',
            date='2026-10-01',
        )

        module.delete()

        assert not Lecture.objects.filter(id=lecture.id).exists()
