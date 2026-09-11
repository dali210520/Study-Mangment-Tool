"""
Tests for PDF study material API endpoints.
"""
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import CustomUser
from apps.courses.models import StudyModule
from apps.materials.models import StudyMaterial
from tests.test_materials_models import make_pdf_bytes


@pytest.fixture(autouse=True)
def media_root(settings, tmp_path):
    """Store uploaded files in a temporary directory during tests."""
    settings.MEDIA_ROOT = tmp_path


@pytest.fixture
def api_client():
    """Fixture providing a DRF API client."""
    return APIClient()


@pytest.fixture
def material_module(authenticated_user):
    """Fixture providing a module for material tests."""
    return StudyModule.objects.create(
        user=authenticated_user,
        name='Databases',
        semester='WS 2026',
    )


def uploaded_pdf(name='database-notes.pdf', text='Relational algebra and SQL joins'):
    """Return an uploaded PDF test file."""
    return SimpleUploadedFile(
        name,
        make_pdf_bytes(text),
        content_type='application/pdf',
    )


@pytest.mark.django_db
@pytest.mark.integration
class TestStudyMaterialAPI:
    """API tests for PDF materials."""

    def test_material_list_requires_authentication(self, api_client):
        response = api_client.get(reverse('material-list'))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_upload_material_extracts_pdf_text(self, api_client, authenticated_user, material_module):
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.post(
            reverse('material-list'),
            {
                'module': material_module.id,
                'title': 'Database Notes',
                'file': uploaded_pdf(text='Relational algebra and SQL joins'),
            },
            format='multipart',
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Database Notes'
        assert response.data['module'] == material_module.id
        assert response.data['module_name'] == material_module.name
        assert response.data['original_filename'] == 'database-notes.pdf'
        assert response.data['page_count'] == 1

        material = StudyMaterial.objects.get(id=response.data['id'])
        assert 'Relational algebra' in material.extracted_text

    def test_upload_material_requires_pdf_file(self, api_client, authenticated_user, material_module):
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.post(
            reverse('material-list'),
            {
                'module': material_module.id,
                'title': 'Bad Upload',
                'file': SimpleUploadedFile('notes.txt', b'not pdf', content_type='text/plain'),
            },
            format='multipart',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'file' in response.data

    def test_upload_material_rejects_other_users_module(self, api_client, authenticated_user):
        other_user = CustomUser.objects.create_user(
            username='materialother',
            email='materialother@example.com',
            password='SecurePass123!',
        )
        other_module = StudyModule.objects.create(user=other_user, name='Private Module')
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.post(
            reverse('material-list'),
            {
                'module': other_module.id,
                'title': 'Private Upload',
                'file': uploaded_pdf(),
            },
            format='multipart',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not StudyMaterial.objects.filter(title='Private Upload').exists()

    def test_list_only_returns_own_materials(self, api_client, authenticated_user, material_module):
        other_user = CustomUser.objects.create_user(
            username='othermaterialowner',
            email='othermaterialowner@example.com',
            password='SecurePass123!',
        )
        other_module = StudyModule.objects.create(user=other_user, name='Other Module')
        own_material = StudyMaterial.objects.create(
            user=authenticated_user,
            module=material_module,
            title='Own Material',
            file=uploaded_pdf('own.pdf'),
            original_filename='own.pdf',
            extracted_text='owned text',
            page_count=1,
        )
        StudyMaterial.objects.create(
            user=other_user,
            module=other_module,
            title='Other Material',
            file=uploaded_pdf('other.pdf'),
            original_filename='other.pdf',
            extracted_text='other text',
            page_count=1,
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(reverse('material-list'))

        assert response.status_code == status.HTTP_200_OK
        assert [material['id'] for material in response.data] == [own_material.id]

    def test_filter_and_search_material_metadata(
        self,
        api_client,
        authenticated_user,
        material_module,
    ):
        other_module = StudyModule.objects.create(user=authenticated_user, name='Algorithms')
        matching_material = StudyMaterial.objects.create(
            user=authenticated_user,
            module=material_module,
            title='SQL Lecture Notes',
            file=uploaded_pdf('sql.pdf'),
            original_filename='sql.pdf',
            extracted_text='relational text',
            page_count=1,
        )
        StudyMaterial.objects.create(
            user=authenticated_user,
            module=other_module,
            title='Graph Notes',
            file=uploaded_pdf('graphs.pdf'),
            original_filename='graphs.pdf',
            extracted_text='graph text',
            page_count=1,
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(
            reverse('material-list'),
            {'module': material_module.id, 'search': 'sql'},
        )

        assert response.status_code == status.HTTP_200_OK
        assert [material['id'] for material in response.data] == [matching_material.id]

    def test_search_inside_extracted_pdf_text(self, api_client, authenticated_user, material_module):
        material = StudyMaterial.objects.create(
            user=authenticated_user,
            module=material_module,
            title='Database Script',
            file=uploaded_pdf('script.pdf'),
            original_filename='script.pdf',
            extracted_text='This script explains relational algebra and SQL joins in detail.',
            page_count=1,
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(reverse('material-search'), {'q': 'relational algebra'})

        assert response.status_code == status.HTTP_200_OK
        assert response.data == [
            {
                'id': material.id,
                'title': 'Database Script',
                'module': material_module.id,
                'module_name': material_module.name,
                'page_count': 1,
                'snippet': 'This script explains relational algebra and SQL joins in detail.',
            }
        ]

    def test_material_search_supports_module_filter(
        self,
        api_client,
        authenticated_user,
        material_module,
    ):
        other_module = StudyModule.objects.create(user=authenticated_user, name='Algorithms')
        matching_material = StudyMaterial.objects.create(
            user=authenticated_user,
            module=material_module,
            title='Database Script',
            file=uploaded_pdf('database.pdf'),
            original_filename='database.pdf',
            extracted_text='shared keyword',
            page_count=1,
        )
        StudyMaterial.objects.create(
            user=authenticated_user,
            module=other_module,
            title='Algorithm Script',
            file=uploaded_pdf('algorithms.pdf'),
            original_filename='algorithms.pdf',
            extracted_text='shared keyword',
            page_count=1,
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(
            reverse('material-search'),
            {'q': 'shared', 'module': material_module.id},
        )

        assert response.status_code == status.HTTP_200_OK
        assert [result['id'] for result in response.data] == [matching_material.id]

    def test_empty_material_search_returns_empty_list(self, api_client, authenticated_user):
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(reverse('material-search'))

        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_update_material_file_reextracts_text(self, api_client, authenticated_user, material_module):
        material = StudyMaterial.objects.create(
            user=authenticated_user,
            module=material_module,
            title='Old Notes',
            file=uploaded_pdf('old.pdf', 'Old PDF text'),
            original_filename='old.pdf',
            extracted_text='Old PDF text',
            page_count=1,
        )
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.patch(
            reverse('material-detail', args=[material.id]),
            {
                'title': 'Updated Notes',
                'file': uploaded_pdf('new.pdf', 'New PDF text with joins'),
            },
            format='multipart',
        )

        assert response.status_code == status.HTTP_200_OK
        material.refresh_from_db()
        assert material.title == 'Updated Notes'
        assert material.original_filename == 'new.pdf'
        assert 'New PDF text with joins' in material.extracted_text

    def test_cannot_access_other_users_material(self, api_client):
        owner = CustomUser.objects.create_user(
            username='materialprivateowner',
            email='materialprivateowner@example.com',
            password='SecurePass123!',
        )
        visitor = CustomUser.objects.create_user(
            username='materialprivatevisitor',
            email='materialprivatevisitor@example.com',
            password='SecurePass123!',
        )
        module = StudyModule.objects.create(user=owner, name='Private Module')
        material = StudyMaterial.objects.create(
            user=owner,
            module=module,
            title='Private Material',
            file=uploaded_pdf('private.pdf'),
            original_filename='private.pdf',
            extracted_text='private text',
            page_count=1,
        )
        api_client.force_authenticate(user=visitor)

        response = api_client.get(reverse('material-detail', args=[material.id]))

        assert response.status_code == status.HTTP_404_NOT_FOUND
