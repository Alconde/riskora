import pytest
from apps.core.mixins import CompanyScopedMixin
from apps.companies.models import Company, CompanyMembership
from apps.workcenters.models import WorkCenter
from tests.factories import (
    CompanyFactory, WorkCenterFactory, UserFactory, CompanyMembershipFactory,
)


class MockModel:
    """Mock model for testing CompanyScopedMixin."""
    def __init__(self):
        self.queryset = None


@pytest.mark.django_db
class TestCompanyScopedMixin:
    def _get_mixin(self):
        mixin = CompanyScopedMixin()
        mixin.company_field_name = 'company'
        mixin.allow_superuser_global = True
        return mixin

    def test_scoped_queryset_filters_by_company(self):
        mixin = self._get_mixin()
        c1 = CompanyFactory()
        c2 = CompanyFactory()
        wc1 = WorkCenterFactory(company=c1)
        wc2 = WorkCenterFactory(company=c2)

        request = type('Request', (), {
            'active_company': c1,
            'company_membership': None,
            'user': UserFactory(),
        })()

        mixin.request = request
        mixin.queryset = WorkCenter.objects.all()

        qs = mixin.scope_queryset_to_company(WorkCenter.objects.all())
        assert qs.count() == 1
        assert wc1 in qs
        assert wc2 not in qs

    def test_superuser_global_access_unfiltered(self):
        mixin = self._get_mixin()
        c1 = CompanyFactory()
        c2 = CompanyFactory()
        WorkCenterFactory(company=c1)
        WorkCenterFactory(company=c2)

        request = type('Request', (), {
            'active_company': c1,
            'company_membership': None,
            'user': UserFactory(is_superuser=True),
        })()

        mixin.request = request
        qs = mixin.scope_queryset_to_company(WorkCenter.objects.all())
        assert qs.count() == 2

    def test_no_active_company_returns_empty(self):
        mixin = self._get_mixin()
        WorkCenterFactory()

        request = type('Request', (), {
            'active_company': None,
            'company_membership': None,
            'user': UserFactory(),
        })()

        mixin.request = request
        qs = mixin.scope_queryset_to_company(WorkCenter.objects.all())
        assert qs.count() == 0

    def test_custom_company_field_name(self):
        mixin = self._get_mixin()
        mixin.company_field_name = 'empresa'

        from apps.risk_assessment.models import EvaluacionRiesgos
        from tests.factories import EvaluacionRiesgosFactory

        c1 = CompanyFactory()
        c2 = CompanyFactory()

        eval1 = EvaluacionRiesgosFactory(empresa=c1)
        eval2 = EvaluacionRiesgosFactory(empresa=c2)

        request = type('Request', (), {
            'active_company': c1,
            'company_membership': None,
            'user': UserFactory(),
        })()

        mixin.request = request
        mixin.queryset = EvaluacionRiesgos.objects.all()
        qs = mixin.scope_queryset_to_company(EvaluacionRiesgos.objects.all())
        assert eval1 in qs
        assert eval2 not in qs
