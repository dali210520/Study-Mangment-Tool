"""
Tests for study material models.
"""
import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.accounts.models import CustomUser
from apps.courses.models import StudyModule
from apps.materials.models import StudyMaterial


@pytest.fixture(autouse=True)
def media_root(settings, tmp_path):
    """Store uploaded files in a temporary directory during tests."""
    settings.MEDIA_ROOT = tmp_path


def make_pdf_bytes(text='Relational algebra and SQL joins'):
    """Create a tiny valid single-page PDF containing text."""
    escaped = text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
    objects = [
        b'1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n',
        b'2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n',
        (
            b'3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] '
            b'/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n'
        ),
        b'4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n',
    ]
    stream = f'BT /F1 12 Tf 72 720 Td ({escaped}) Tj ET'.encode('latin-1')
    objects.append(
        b'5 0 obj\n<< /Length ' + str(len(stream)).encode()
        + b' >>\nstream\n' + stream + b'\nendstream\nendobj\n'
    )

    pdf = bytearray(b'%PDF-1.4\n')
    offsets = [0]
    for pdf_object in objects:
        offsets.append(len(pdf))
        pdf.extend(pdf_object)

    xref_offset = len(pdf)
    pdf.extend(f'xref\n0 {len(objects) + 1}\n'.encode())
    pdf.extend(b'0000000000 65535 f \n')
    for offset in offsets[1:]:
        pdf.extend(f'{offset:010d} 00000 n \n'.encode())
    pdf.extend(
        f'trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n'
        f'startxref\n{xref_offset}\n%%EOF\n'.encode()
    )
    return bytes(pdf)


@pytest.mark.django_db
@pytest.mark.unit
class TestStudyMaterialModel:
    """Test cases for the StudyMaterial model."""

    def test_material_str(self, authenticated_user):
        module = StudyModule.objects.create(user=authenticated_user, name='Databases')
        material = StudyMaterial.objects.create(
            user=authenticated_user,
            module=module,
            title='SQL Notes',
            file=SimpleUploadedFile('sql.pdf', make_pdf_bytes(), content_type='application/pdf'),
            original_filename='sql.pdf',
        )

        assert str(material) == 'SQL Notes'

    def test_material_rejects_non_pdf_file(self, authenticated_user):
        module = StudyModule.objects.create(user=authenticated_user, name='Databases')

        with pytest.raises(ValidationError):
            StudyMaterial.objects.create(
                user=authenticated_user,
                module=module,
                title='Not a PDF',
                file=SimpleUploadedFile('notes.txt', b'hello', content_type='text/plain'),
                original_filename='notes.txt',
            )

    def test_material_module_must_belong_to_same_user(self, authenticated_user):
        other_user = CustomUser.objects.create_user(
            username='materialowner',
            email='materialowner@example.com',
            password='SecurePass123!',
        )
        module = StudyModule.objects.create(user=other_user, name='Private Module')

        with pytest.raises(ValidationError):
            StudyMaterial.objects.create(
                user=authenticated_user,
                module=module,
                title='Invalid material',
                file=SimpleUploadedFile('invalid.pdf', make_pdf_bytes(), content_type='application/pdf'),
                original_filename='invalid.pdf',
            )
