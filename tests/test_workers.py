import pytest
from django.db import IntegrityError
from apps.workers.models import Worker, JobPosition
from tests.factories import (
    CompanyFactory, WorkerFactory, JobPositionFactory, WorkCenterFactory, UserFactory,
)


@pytest.mark.django_db
class TestJobPosition:
    def test_create_job_position(self):
        jp = JobPositionFactory(name='Carnicero', department='Producción')
        assert jp.name == 'Carnicero'
        assert jp.department == 'Producción'
        assert jp.status == 'active'

    def test_unique_together_company_name(self):
        company = CompanyFactory()
        JobPositionFactory(company=company, name='Carnicero')
        with pytest.raises(IntegrityError):
            JobPositionFactory(company=company, name='Carnicero')

    def test_str_representation(self):
        jp = JobPositionFactory(name='Pastelero')
        assert 'Pastelero' in str(jp)

    def test_status_choices(self):
        for status in ['active', 'inactive']:
            jp = JobPositionFactory(status=status)
            assert jp.status == status

    def test_cascade_delete_company(self):
        company = CompanyFactory()
        JobPositionFactory(company=company)
        company.delete()
        assert JobPosition.objects.count() == 0


@pytest.mark.django_db
class TestWorker:
    def test_create_worker(self):
        worker = WorkerFactory(
            first_name='Juan',
            last_name='García',
            national_id='12345678A',
            employee_code='EMP-001',
        )
        assert worker.first_name == 'Juan'
        assert worker.last_name == 'García'
        assert worker.national_id == '12345678A'
        assert worker.employee_code == 'EMP-001'
        assert worker.employment_status == 'active'

    def test_national_id_unique(self):
        WorkerFactory(national_id='11111111A')
        with pytest.raises(IntegrityError):
            WorkerFactory(national_id='11111111A')

    def test_str_representation(self):
        worker = WorkerFactory(first_name='María', last_name='López')
        assert str(worker) == 'María López'

    def test_employment_status_choices(self):
        for status in ['active', 'leave', 'inactive']:
            worker = WorkerFactory(employment_status=status)
            assert worker.employment_status == status

    def test_optional_user_link(self):
        user = UserFactory()
        worker = WorkerFactory(user=user)
        assert worker.user == user

    def test_sensitive_worker_flag(self):
        worker = WorkerFactory(especially_sensitive=True, temporary_worker=True)
        assert worker.especially_sensitive is True
        assert worker.temporary_worker is True

    def test_cascade_delete_company(self):
        company = CompanyFactory()
        WorkerFactory(company=company)
        WorkerFactory(company=company)
        count_before = Worker.objects.count()
        company.delete()
        assert Worker.objects.count() == count_before - 2
