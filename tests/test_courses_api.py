"""
Tests for module and lecture API endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import CustomUser
from apps.courses.models import Lecture, StudyModule


@pytest.fixture
def api_client():
    """Fixture providing a DRF API client."""
    return APIClient()


@pytest.fixture
def study_module(authenticated_user):
    """Fixture providing a study module owned by the authenticated user."""
    return StudyModule.objects.create(
        user=authenticated_user,
        name='Software Engineering',
        semester='WS 2026',
        lecturer='Prof. Test',
    )


@pytest.mark.django_db
@pytest.mark.integration
class TestStudyModuleAPI:
    """API tests for study modules."""

    def test_module_list_requires_authentication(self, api_client):
        response = api_client.get(reverse('module-list'))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_module_for_authenticated_user(self, api_client, authenticated_user):
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.post(
            reverse('module-list'),
            {
                'name': 'Databases',
                'semester': 'SS 2027',
                'lecturer': 'Dr. Query',
                'description': 'Relational databases and SQL.',
            },
            format='json',
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Databases'
        assert response.data['lecture_count'] == 0
        assert StudyModule.objects.filter(
            user=authenticated_user,
            name='Databases',
        ).exists()

    def test_list_only_returns_own_modules(self, api_client, authenticated_user):
        other_user = CustomUser.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='SecurePass123!',
        )
        own_module = StudyModule.objects.create(
            user=authenticated_user,
            name='Own Module',
        )
        StudyModule.objects.create(
            user=other_user,
            name='Other Module',
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(reverse('module-list'))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == own_module.id

    def test_search_and_order_modules(self, api_client, authenticated_user):
        StudyModule.objects.create(
            user=authenticated_user,
            name='Algorithms',
            semester='WS 2026',
            lecturer='Prof. Sort',
            description='Graph theory and runtime complexity.',
        )
        StudyModule.objects.create(
            user=authenticated_user,
            name='Databases',
            semester='SS 2027',
            lecturer='Dr. Query',
            description='SQL and transactions.',
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(
            reverse('module-list'),
            {'search': 'sql', 'ordering': '-name'},
        )

        assert response.status_code == status.HTTP_200_OK
        assert [module['name'] for module in response.data] == ['Databases']

    def test_update_own_module(self, api_client, authenticated_user, study_module):
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.patch(
            reverse('module-detail', args=[study_module.id]),
            {'lecturer': 'Prof. Updated'},
            format='json',
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['lecturer'] == 'Prof. Updated'

    def test_cannot_access_other_users_module(self, api_client):
        owner = CustomUser.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='SecurePass123!',
        )
        visitor = CustomUser.objects.create_user(
            username='visitor',
            email='visitor@example.com',
            password='SecurePass123!',
        )
        module = StudyModule.objects.create(user=owner, name='Private Module')
        api_client.force_authenticate(user=visitor)

        response = api_client.get(reverse('module-detail', args=[module.id]))

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.integration
class TestLectureAPI:
    """API tests for lectures."""

    def test_create_lecture_for_owned_module(self, api_client, authenticated_user, study_module):
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.post(
            reverse('lecture-list', args=[study_module.id]),
            {
                'title': 'Clean Architecture',
                'date': '2026-10-20',
                'notes': 'Layered Django structure.',
            },
            format='json',
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['module'] == study_module.id
        assert response.data['module_name'] == study_module.name
        assert Lecture.objects.filter(module=study_module, title='Clean Architecture').exists()

    def test_list_lectures_for_owned_module(self, api_client, authenticated_user, study_module):
        Lecture.objects.create(
            module=study_module,
            title='Second Lecture',
            date='2026-10-14',
        )
        Lecture.objects.create(
            module=study_module,
            title='First Lecture',
            date='2026-10-07',
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(reverse('lecture-list', args=[study_module.id]))

        assert response.status_code == status.HTTP_200_OK
        assert [lecture['title'] for lecture in response.data] == [
            'First Lecture',
            'Second Lecture',
        ]

    def test_search_filter_and_order_lectures(self, api_client, authenticated_user, study_module):
        Lecture.objects.create(
            module=study_module,
            title='Clean Architecture',
            date='2026-10-20',
            notes='Layered Django structure.',
        )
        Lecture.objects.create(
            module=study_module,
            title='Testing Basics',
            date='2026-10-10',
            notes='pytest and fixtures.',
        )
        Lecture.objects.create(
            module=study_module,
            title='Advanced Testing',
            date='2026-11-01',
            notes='mocking and coverage.',
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(
            reverse('lecture-list', args=[study_module.id]),
            {
                'search': 'testing',
                'date_before': '2026-10-31',
                'ordering': '-date',
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert [lecture['title'] for lecture in response.data] == ['Testing Basics']

    def test_create_lecture_rejects_other_users_module(self, api_client):
        owner = CustomUser.objects.create_user(
            username='moduleowner',
            email='moduleowner@example.com',
            password='SecurePass123!',
        )
        visitor = CustomUser.objects.create_user(
            username='modulevisitor',
            email='modulevisitor@example.com',
            password='SecurePass123!',
        )
        module = StudyModule.objects.create(user=owner, name='Private Module')
        api_client.force_authenticate(user=visitor)

        response = api_client.post(
            reverse('lecture-list', args=[module.id]),
            {'title': 'Unauthorized Lecture', 'date': '2026-10-20'},
            format='json',
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert not Lecture.objects.filter(title='Unauthorized Lecture').exists()

    def test_update_own_lecture(self, api_client, authenticated_user, study_module):
        lecture = Lecture.objects.create(
            module=study_module,
            title='Old Title',
            date='2026-10-20',
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.patch(
            reverse('lecture-detail', args=[lecture.id]),
            {'title': 'Updated Title'},
            format='json',
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Updated Title'

    def test_cannot_access_other_users_lecture(self, api_client):
        owner = CustomUser.objects.create_user(
            username='lectureowner',
            email='lectureowner@example.com',
            password='SecurePass123!',
        )
        visitor = CustomUser.objects.create_user(
            username='lecturevisitor',
            email='lecturevisitor@example.com',
            password='SecurePass123!',
        )
        module = StudyModule.objects.create(user=owner, name='Private Module')
        lecture = Lecture.objects.create(
            module=module,
            title='Private Lecture',
            date='2026-10-20',
        )
        api_client.force_authenticate(user=visitor)

        response = api_client.get(reverse('lecture-detail', args=[lecture.id]))

        assert response.status_code == status.HTTP_404_NOT_FOUND
