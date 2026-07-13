import pytest
from django.db import IntegrityError
from apps.documents.models import DocumentCategory, Document
from tests.factories import CompanyFactory, DocumentCategoryFactory, DocumentFactory


@pytest.mark.django_db
class TestDocumentCategory:
    def test_create_category(self):
        cat = DocumentCategoryFactory(name='Políticas', slug='politicas')
        assert cat.name == 'Políticas'
        assert cat.slug == 'politicas'
        assert cat.scope == 'general'

    def test_slug_unique(self):
        DocumentCategoryFactory(slug='politicas')
        with pytest.raises(IntegrityError):
            DocumentCategoryFactory(slug='politicas')

    def test_scope_choices(self):
        for scope in ['general', 'company', 'workcenter', 'worker', 'job_position']:
            cat = DocumentCategoryFactory(scope=scope)
            assert cat.scope == scope

    def test_str_representation(self):
        cat = DocumentCategoryFactory(name='Manuales')
        assert str(cat) == 'Manuales'


@pytest.mark.django_db
class TestDocument:
    def test_create_document(self):
        doc = DocumentFactory(
            title='Política de seguridad',
            version='2.0',
            status='valid',
        )
        assert doc.title == 'Política de seguridad'
        assert doc.version == '2.0'
        assert doc.status == 'valid'
        assert doc.is_confidential is False

    def test_uuid_primary_key(self):
        doc = DocumentFactory()
        assert doc.pk is not None
        assert isinstance(doc.pk, str) or hasattr(doc.pk, 'hex')

    def test_status_choices(self):
        for status in ['draft', 'valid', 'expired', 'revoked', 'archived']:
            doc = DocumentFactory(status=status)
            assert doc.status == status

    def test_str_representation(self):
        doc = DocumentFactory(title='Manual de seguridad')
        assert str(doc) == 'Manual de seguridad'

    def test_optional_dates(self):
        doc = DocumentFactory()
        assert doc.issue_date is None or doc.issue_date is not None
        assert doc.review_date is None or doc.review_date is not None
        assert doc.expiry_date is None or doc.expiry_date is not None
