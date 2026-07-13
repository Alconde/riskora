import pytest
from datetime import timedelta
from django.utils import timezone
from apps.companies.models import Company, CompanyMembership
from apps.workcenters.models import WorkCenter
from apps.workers.models import Worker, JobPosition
from apps.risk_assessment.models import EvaluacionRiesgos, ItemEvaluacionRiesgos
from apps.corrective_actions.models import NoConformidad, AccionCorrectiva
from apps.training.models import TrainingRecord
from tests.factories import (
    UserFactory, CompanyFactory, CompanyMembershipFactory,
    WorkCenterFactory, JobPositionFactory, WorkerFactory,
    EvaluacionRiesgosFactory, ItemEvaluacionRiesgosFactory,
    NoConformidadFactory, AccionCorrectivaFactory,
    TrainingCategoryFactory, TrainingCourseFactory, TrainingRecordFactory,
)


@pytest.mark.django_db
class TestCompanySetupFlow:
    """Test the full flow: create company → center → worker."""

    def test_full_setup(self):
        company = CompanyFactory(legal_name='Pastelería Test')
        assert company.status == 'active'

        center = WorkCenterFactory(company=company, name='Tienda Principal')
        assert center.company == company

        position = JobPositionFactory(company=company, name='Repostero')
        worker = WorkerFactory(
            company=company,
            work_center=center,
            job_position=position,
            first_name='Carlos',
            last_name='Ruiz',
        )
        assert worker.company == company
        assert worker.work_center == center
        assert worker.job_position == position

        membership = CompanyMembershipFactory(
            user=UserFactory(),
            company=company,
            role=CompanyMembership.Role.COMPANY_ADMIN,
        )
        assert membership.user is not None
        assert membership.company == company


@pytest.mark.django_db
class TestRiskAssessmentFlow:
    """Test the full risk assessment flow."""

    def test_full_evaluation(self):
        company = CompanyFactory()
        center = WorkCenterFactory(company=company)
        position = JobPositionFactory(company=company)

        ev = EvaluacionRiesgosFactory(
            empresa=company,
            centro_trabajo=center,
            titulo='Evaluación Anual',
            revisado_por=UserFactory(),
        )

        item1 = ItemEvaluacionRiesgosFactory(
            evaluacion=ev,
            puesto_trabajo=position,
            probabilidad=3,
            severidad=3,
            factor_riesgo_condicion='Ruido excesivo',
        )
        assert item1.grado_riesgo == 9
        assert item1.nivel_riesgo == 'muy_alto'

        item2 = ItemEvaluacionRiesgosFactory(
            evaluacion=ev,
            puesto_trabajo=position,
            probabilidad=1,
            severidad=1,
            factor_riesgo_condicion='Riesgo mínimo',
        )
        assert item2.grado_riesgo == 1
        assert item2.nivel_riesgo == 'muy_bajo'

        assert ev.total_items == 2
        assert ev.items_requieren_accion == 1


@pytest.mark.django_db
class TestNCFlow:
    """Test the full non-conformity flow."""

    def test_nc_with_corrective_action(self):
        company = CompanyFactory()
        nc = NoConformidadFactory(
            empresa=company,
            titulo='Incumplimiento norma',
            gravedad='importante',
        )

        ac = AccionCorrectivaFactory(
            no_conformidad=nc,
            descripcion='Implementar nuevo procedimiento',
            fecha_limite=timezone.localdate() + timedelta(days=15),
        )

        assert nc.acciones_correctivas.count() == 1
        assert ac.no_conformidad == nc
        assert nc.esta_vencida is False


@pytest.mark.django_db
class TestTrainingFlow:
    """Test the full training flow."""

    def test_training_record_creation(self):
        company = CompanyFactory()
        worker = WorkerFactory(company=company)
        category = TrainingCategoryFactory(name='Seguridad')
        course = TrainingCourseFactory(
            company=company,
            category=category,
            name='Prevención de riesgos',
            requires_renewal=True,
            validity_value=12,
            validity_unit='months',
        )

        record = TrainingRecordFactory(
            company=company,
            worker=worker,
            course=course,
            status='planned',
            planned_date=timezone.localdate() + timedelta(days=30),
        )

        assert record.worker == worker
        assert record.course == company.training_courses.first()
        assert record.status == 'planned'


@pytest.mark.django_db
class TestMultiCompanyIsolation:
    """Test that data isolation works between companies."""

    def test_different_companies_see_different_data(self):
        c1 = CompanyFactory()
        c2 = CompanyFactory()

        WorkCenterFactory(company=c1, name='Centro C1')
        WorkCenterFactory(company=c2, name='Centro C2')

        from apps.workcenters.models import WorkCenter
        assert WorkCenter.objects.filter(company=c1).count() == 1
        assert WorkCenter.objects.filter(company=c2).count() == 1
        assert WorkCenter.objects.filter(company=c1).first().name == 'Centro C1'
        assert WorkCenter.objects.filter(company=c2).first().name == 'Centro C2'
