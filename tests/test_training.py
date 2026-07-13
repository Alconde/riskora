import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from apps.training.models import (
    TrainingCategory, TrainingCourse, TrainingRecord,
)
from tests.factories import (
    CompanyFactory, TrainingCategoryFactory, TrainingCourseFactory,
    TrainingRecordFactory, WorkerFactory, JobPositionFactory,
)


@pytest.mark.django_db
class TestTrainingCategory:
    def test_create_category(self):
        cat = TrainingCategoryFactory(name='Seguridad Industrial', code='SI')
        assert cat.name == 'Seguridad Industrial'
        assert cat.code == 'SI'
        assert cat.is_active is True

    def test_name_unique(self):
        TrainingCategoryFactory(name='Única')
        with pytest.raises(IntegrityError):
            TrainingCategoryFactory(name='Única')

    def test_str_representation(self):
        cat = TrainingCategoryFactory(name='Prevención')
        assert str(cat) == 'Prevención'


@pytest.mark.django_db
class TestTrainingCourse:
    def test_create_course(self):
        course = TrainingCourseFactory(
            name='Manipulador de alimentos',
            modality='presential',
            duration_hours=8,
            is_mandatory=True,
        )
        assert course.name == 'Manipulador de alimentos'
        assert course.modality == 'presential'
        assert course.duration_hours == 8
        assert course.is_mandatory is True
        assert course.status == 'active'

    def test_unique_together_company_name(self):
        company = CompanyFactory()
        TrainingCourseFactory(company=company, name='Curso A')
        with pytest.raises(IntegrityError):
            TrainingCourseFactory(company=company, name='Curso A')

    def test_modality_choices(self):
        for mod in ['presential', 'online', 'mixed']:
            course = TrainingCourseFactory(modality=mod)
            assert course.modality == mod

    def test_requires_renewal_fields(self):
        course = TrainingCourseFactory(
            requires_renewal=True,
            validity_value=12,
            validity_unit='months',
        )
        assert course.requires_renewal is True
        assert course.validity_value == 12
        assert course.validity_unit == 'months'

    def test_str_representation(self):
        course = TrainingCourseFactory(name='Curso Test')
        assert 'Curso Test' in str(course)


@pytest.mark.django_db
class TestTrainingRecord:
    def test_create_record(self):
        record = TrainingRecordFactory(
            status='planned',
            trainer_name='Dr. López',
        )
        assert record.status == 'planned'
        assert record.trainer_name == 'Dr. López'

    def test_status_choices(self):
        for status in ['planned', 'in_progress', 'completed', 'expired', 'cancelled']:
            record = TrainingRecordFactory(status=status)
            assert record.status == status

    def test_effectiveness_fields(self):
        record = TrainingRecordFactory(
            effectiveness_validated=True,
            effectiveness_notes='Cumple objetivos',
        )
        assert record.effectiveness_validated is True
        assert record.effectiveness_notes == 'Cumple objetivos'

    def test_str_representation(self):
        record = TrainingRecordFactory()
        assert record.worker.first_name in str(record) or str(record.worker.pk) in str(record)
