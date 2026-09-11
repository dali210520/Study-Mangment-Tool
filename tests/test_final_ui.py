"""
Tests for the final server-rendered UI pages.
"""
from datetime import timedelta

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import CustomUser
from apps.courses.models import StudyModule
from apps.deadlines.models import Deadline
from apps.materials.models import StudyMaterial
from apps.plans.models import StudyPlanEntry
from apps.tasks.models import Task
from tests.test_materials_models import make_pdf_bytes


@pytest.fixture(autouse=True)
def media_root(settings, tmp_path):
    """Store uploaded files in a temporary directory during tests."""
    settings.MEDIA_ROOT = tmp_path


def uploaded_pdf(name='script.pdf', text='Relational algebra and SQL joins'):
    """Return an uploaded PDF test file."""
    return SimpleUploadedFile(
        name,
        make_pdf_bytes(text),
        content_type='application/pdf',
    )


@pytest.mark.django_db
@pytest.mark.integration
class TestProgressUI:
    """UI tests for the progress page."""

    def test_progress_requires_login(self, client):
        response = client.get(reverse('ui-progress'))

        assert response.status_code == 302
        assert response['Location'].startswith('/login/')

    def test_progress_renders_owned_summary(self, client, authenticated_user):
        today = timezone.localdate()
        module = StudyModule.objects.create(user=authenticated_user, name='Databases')
        Task.objects.create(
            user=authenticated_user,
            module=module,
            title='Done task',
            due_date=today,
            status=Task.Status.DONE,
        )
        Deadline.objects.create(
            user=authenticated_user,
            module=module,
            title='Exam',
            date=today + timedelta(days=2),
        )
        StudyPlanEntry.objects.create(
            user=authenticated_user,
            module=module,
            topic='SQL review',
            planned_date=today,
            duration_minutes=90,
            status=StudyPlanEntry.Status.DONE,
        )
        client.force_login(authenticated_user)

        response = client.get(reverse('ui-progress'))

        assert response.status_code == 200
        content = response.content.decode()
        assert 'Fortschritt' in content
        assert 'SQL review' in content
        assert 'Exam' in content
        assert '90' in content


@pytest.mark.django_db
@pytest.mark.integration
class TestStudyMaterialUI:
    """UI tests for PDF study material pages."""

    def test_material_list_requires_login(self, client):
        response = client.get(reverse('ui-material-list'))

        assert response.status_code == 302
        assert response['Location'].startswith('/login/')

    def test_material_list_only_shows_owned_materials(self, client, authenticated_user):
        other_user = CustomUser.objects.create_user(
            username='materialuiother',
            email='materialuiother@example.com',
            password='SecurePass123!',
        )
        module = StudyModule.objects.create(user=authenticated_user, name='Databases')
        other_module = StudyModule.objects.create(user=other_user, name='Other')
        StudyMaterial.objects.create(
            user=authenticated_user,
            module=module,
            title='Own Script',
            file=uploaded_pdf('own.pdf'),
            original_filename='own.pdf',
            extracted_text='own text',
            page_count=1,
        )
        StudyMaterial.objects.create(
            user=other_user,
            module=other_module,
            title='Private Script',
            file=uploaded_pdf('private.pdf'),
            original_filename='private.pdf',
            extracted_text='private text',
            page_count=1,
        )
        client.force_login(authenticated_user)

        response = client.get(reverse('ui-material-list'))

        assert response.status_code == 200
        content = response.content.decode()
        assert 'Own Script' in content
        assert 'Private Script' not in content

    def test_upload_material_from_ui_extracts_text(self, client, authenticated_user):
        module = StudyModule.objects.create(user=authenticated_user, name='Databases')
        client.force_login(authenticated_user)

        response = client.post(
            reverse('ui-material-create'),
            {
                'module': module.id,
                'title': 'Database Script',
                'file': uploaded_pdf(text='Database normalization and SQL joins'),
            },
        )

        material = StudyMaterial.objects.get(title='Database Script')
        assert response.status_code == 302
        assert response['Location'] == reverse('ui-material-list')
        assert material.user == authenticated_user
        assert material.module == module
        assert 'normalization' in material.extracted_text
        assert material.page_count == 1

    def test_upload_material_rejects_non_pdf(self, client, authenticated_user):
        module = StudyModule.objects.create(user=authenticated_user, name='Databases')
        client.force_login(authenticated_user)

        response = client.post(
            reverse('ui-material-create'),
            {
                'module': module.id,
                'title': 'Bad Script',
                'file': SimpleUploadedFile('notes.txt', b'not pdf', content_type='text/plain'),
            },
        )

        assert response.status_code == 200
        assert not StudyMaterial.objects.filter(title='Bad Script').exists()

    def test_material_list_filters_by_module_and_query(self, client, authenticated_user):
        selected_module = StudyModule.objects.create(user=authenticated_user, name='Databases')
        other_module = StudyModule.objects.create(user=authenticated_user, name='Algorithms')
        StudyMaterial.objects.create(
            user=authenticated_user,
            module=selected_module,
            title='SQL Script',
            file=uploaded_pdf('sql.pdf'),
            original_filename='sql.pdf',
            extracted_text='sql text',
            page_count=1,
        )
        StudyMaterial.objects.create(
            user=authenticated_user,
            module=other_module,
            title='Graph Script',
            file=uploaded_pdf('graph.pdf'),
            original_filename='graph.pdf',
            extracted_text='graph text',
            page_count=1,
        )
        client.force_login(authenticated_user)

        response = client.get(
            reverse('ui-material-list'),
            {'q': 'sql', 'module': selected_module.id},
        )

        assert response.status_code == 200
        content = response.content.decode()
        assert 'SQL Script' in content
        assert 'Graph Script' not in content

    def test_update_and_delete_material_from_ui(self, client, authenticated_user):
        module = StudyModule.objects.create(user=authenticated_user, name='Databases')
        material = StudyMaterial.objects.create(
            user=authenticated_user,
            module=module,
            title='Old Script',
            file=uploaded_pdf('old.pdf', 'old text'),
            original_filename='old.pdf',
            extracted_text='old text',
            page_count=1,
        )
        client.force_login(authenticated_user)

        update_response = client.post(
            reverse('ui-material-update', args=[material.id]),
            {
                'module': module.id,
                'title': 'Updated Script',
                'file': uploaded_pdf('new.pdf', 'new searchable text'),
            },
        )

        material.refresh_from_db()
        assert update_response.status_code == 302
        assert material.title == 'Updated Script'
        assert 'searchable' in material.extracted_text

        delete_response = client.post(reverse('ui-material-delete', args=[material.id]))

        assert delete_response.status_code == 302
        assert not StudyMaterial.objects.filter(id=material.id).exists()


@pytest.mark.django_db
@pytest.mark.integration
class TestMaterialSearchUI:
    """UI tests for the PDF text search page."""

    def test_search_requires_login(self, client):
        response = client.get(reverse('ui-search'))

        assert response.status_code == 302
        assert response['Location'].startswith('/login/')

    def test_search_finds_owned_pdf_text(self, client, authenticated_user):
        module = StudyModule.objects.create(user=authenticated_user, name='Databases')
        StudyMaterial.objects.create(
            user=authenticated_user,
            module=module,
            title='Database Script',
            file=uploaded_pdf('database.pdf'),
            original_filename='database.pdf',
            extracted_text='This chapter explains relational algebra and SQL joins.',
            page_count=1,
        )
        client.force_login(authenticated_user)

        response = client.get(reverse('ui-search'), {'q': 'relational algebra'})

        assert response.status_code == 200
        content = response.content.decode()
        assert 'Database Script' in content
        assert 'relational algebra' in content

    def test_search_filters_by_module(self, client, authenticated_user):
        selected_module = StudyModule.objects.create(user=authenticated_user, name='Databases')
        other_module = StudyModule.objects.create(user=authenticated_user, name='Algorithms')
        StudyMaterial.objects.create(
            user=authenticated_user,
            module=selected_module,
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
            file=uploaded_pdf('algorithm.pdf'),
            original_filename='algorithm.pdf',
            extracted_text='shared keyword',
            page_count=1,
        )
        client.force_login(authenticated_user)

        response = client.get(
            reverse('ui-search'),
            {'q': 'shared', 'module': selected_module.id},
        )

        assert response.status_code == 200
        content = response.content.decode()
        assert 'Database Script' in content
        assert 'Algorithm Script' not in content
