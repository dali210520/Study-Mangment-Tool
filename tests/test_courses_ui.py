"""
Tests for the server-rendered modules and lectures UI.
"""
import pytest
from django.urls import reverse

from apps.accounts.models import CustomUser
from apps.courses.models import Lecture, StudyModule


@pytest.mark.django_db
@pytest.mark.integration
class TestModuleUI:
    """UI tests for study module pages."""

    def test_module_list_requires_login(self, client):
        response = client.get(reverse('ui-module-list'))

        assert response.status_code == 302
        assert response['Location'].startswith('/login/')

    def test_module_list_only_shows_owned_modules(self, client, authenticated_user):
        other_user = CustomUser.objects.create_user(
            username='moduleuiother',
            email='moduleuiother@example.com',
            password='SecurePass123!',
        )
        StudyModule.objects.create(user=authenticated_user, name='Databases')
        StudyModule.objects.create(user=other_user, name='Private Module')
        client.force_login(authenticated_user)

        response = client.get(reverse('ui-module-list'))

        assert response.status_code == 200
        content = response.content.decode()
        assert 'Databases' in content
        assert 'Private Module' not in content

    def test_create_module_from_ui(self, client, authenticated_user):
        client.force_login(authenticated_user)

        response = client.post(
            reverse('ui-module-create'),
            {
                'name': 'Software Engineering',
                'semester': 'SS 2027',
                'lecturer': 'Prof. Schmidt',
                'description': 'Requirements and architecture.',
            },
        )

        module = StudyModule.objects.get(name='Software Engineering')
        assert response.status_code == 302
        assert response['Location'] == reverse('ui-module-detail', args=[module.id])
        assert module.user == authenticated_user

    def test_update_and_delete_module_from_ui(self, client, authenticated_user):
        module = StudyModule.objects.create(user=authenticated_user, name='Old Name')
        client.force_login(authenticated_user)

        update_response = client.post(
            reverse('ui-module-update', args=[module.id]),
            {
                'name': 'New Name',
                'semester': 'WS 2027',
                'lecturer': 'Prof. Updated',
                'description': 'Updated description.',
            },
        )

        module.refresh_from_db()
        assert update_response.status_code == 302
        assert module.name == 'New Name'

        delete_response = client.post(reverse('ui-module-delete', args=[module.id]))

        assert delete_response.status_code == 302
        assert not StudyModule.objects.filter(id=module.id).exists()

    def test_cannot_access_other_users_module_ui(self, client, authenticated_user):
        other_user = CustomUser.objects.create_user(
            username='moduleownerui',
            email='moduleownerui@example.com',
            password='SecurePass123!',
        )
        module = StudyModule.objects.create(user=other_user, name='Hidden Module')
        client.force_login(authenticated_user)

        response = client.get(reverse('ui-module-detail', args=[module.id]))

        assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.integration
class TestLectureUI:
    """UI tests for lecture pages."""

    def test_module_detail_lists_lectures(self, client, authenticated_user):
        module = StudyModule.objects.create(user=authenticated_user, name='Algorithms')
        Lecture.objects.create(module=module, title='Sorting', date='2027-01-10')
        client.force_login(authenticated_user)

        response = client.get(reverse('ui-module-detail', args=[module.id]))

        assert response.status_code == 200
        content = response.content.decode()
        assert 'Algorithms' in content
        assert 'Sorting' in content

    def test_create_lecture_from_module_ui(self, client, authenticated_user):
        module = StudyModule.objects.create(user=authenticated_user, name='Databases')
        client.force_login(authenticated_user)

        response = client.post(
            reverse('ui-lecture-create', args=[module.id]),
            {
                'title': 'Indexes',
                'date': '2027-01-12',
                'notes': 'B-trees and query plans.',
            },
        )

        assert response.status_code == 302
        assert response['Location'] == reverse('ui-module-detail', args=[module.id])
        assert Lecture.objects.filter(module=module, title='Indexes').exists()

    def test_update_and_delete_lecture_from_ui(self, client, authenticated_user):
        module = StudyModule.objects.create(user=authenticated_user, name='Math')
        lecture = Lecture.objects.create(module=module, title='Old Lecture', date='2027-01-10')
        client.force_login(authenticated_user)

        update_response = client.post(
            reverse('ui-lecture-update', args=[lecture.id]),
            {
                'title': 'Updated Lecture',
                'date': '2027-01-11',
                'notes': 'Updated notes.',
            },
        )

        lecture.refresh_from_db()
        assert update_response.status_code == 302
        assert lecture.title == 'Updated Lecture'

        delete_response = client.post(reverse('ui-lecture-delete', args=[lecture.id]))

        assert delete_response.status_code == 302
        assert not Lecture.objects.filter(id=lecture.id).exists()

    def test_lecture_list_searches_owned_lectures(self, client, authenticated_user):
        module = StudyModule.objects.create(user=authenticated_user, name='Databases')
        other_module = StudyModule.objects.create(user=authenticated_user, name='Algorithms')
        Lecture.objects.create(module=module, title='SQL Joins', date='2027-01-10')
        Lecture.objects.create(module=other_module, title='Sorting', date='2027-01-11')
        client.force_login(authenticated_user)

        response = client.get(reverse('ui-lecture-list'), {'q': 'sql'})

        assert response.status_code == 200
        content = response.content.decode()
        assert 'SQL Joins' in content
        assert 'Sorting' not in content

    def test_cannot_create_lecture_for_other_users_module(self, client, authenticated_user):
        other_user = CustomUser.objects.create_user(
            username='lectureownerui',
            email='lectureownerui@example.com',
            password='SecurePass123!',
        )
        module = StudyModule.objects.create(user=other_user, name='Private Module')
        client.force_login(authenticated_user)

        response = client.post(
            reverse('ui-lecture-create', args=[module.id]),
            {'title': 'Invalid', 'date': '2027-01-10'},
        )

        assert response.status_code == 404
        assert not Lecture.objects.filter(title='Invalid').exists()
