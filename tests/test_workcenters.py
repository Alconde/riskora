import pytest
from django.db import IntegrityError
from apps.workcenters.models import WorkCenter
from tests.factories import CompanyFactory, WorkCenterFactory


@pytest.mark.django_db
class TestWorkCenter:
    def test_create_workcenter(self):
        wc = WorkCenterFactory(
            name='Central',
            code='CEN-001',
            city='Barcelona',
            worker_count=25,
            risk_level='high',
        )
        assert wc.name == 'Central'
        assert wc.code == 'CEN-001'
        assert wc.city == 'Barcelona'
        assert wc.worker_count == 25
        assert wc.risk_level == 'high'
        assert wc.is_active is True

    def test_unique_together_company_name(self):
        company = CompanyFactory()
        WorkCenterFactory(company=company, name='Principal')
        with pytest.raises(IntegrityError):
            WorkCenterFactory(company=company, name='Principal')

    def test_different_company_same_name_ok(self):
        c1 = CompanyFactory()
        c2 = CompanyFactory()
        wc1 = WorkCenterFactory(company=c1, name='Principal')
        wc2 = WorkCenterFactory(company=c2, name='Principal')
        assert wc1.pk != wc2.pk

    def test_str_representation(self):
        wc = WorkCenterFactory(name='Fábrica Norte')
        assert 'Fábrica Norte' in str(wc)

    def test_risk_level_choices(self):
        for level in ['low', 'medium', 'high', 'very_high']:
            wc = WorkCenterFactory(risk_level=level)
            assert wc.risk_level == level

    def test_optional_fields(self):
        wc = WorkCenterFactory(
            address='Avda. Industrial 10',
            postal_code='08001',
            province='Barcelona',
            contact_person='Ana López',
            contact_phone='934567890',
            activity='Manufactura',
        )
        assert wc.address == 'Avda. Industrial 10'
        assert wc.contact_person == 'Ana López'

    def test_cascade_delete_company(self):
        company = CompanyFactory()
        WorkCenterFactory(company=company)
        WorkCenterFactory(company=company)
        count_before = WorkCenter.objects.count()
        company.delete()
        assert WorkCenter.objects.count() == count_before - 2
