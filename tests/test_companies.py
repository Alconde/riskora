import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from apps.companies.models import Company, CompanyMembership
from tests.factories import (
    CompanyFactory, CompanyMembershipFactory, UserFactory, SuperUserFactory,
)

pytestmark = pytest.mark.django_db


@pytest.mark.django_db
class TestCompany:
    def test_create_company(self):
        company = CompanyFactory(
            legal_name='Test Corp',
            trade_name='Test',
            tax_id='B99999999',
        )
        assert company.legal_name == 'Test Corp'
        assert company.trade_name == 'Test'
        assert company.tax_id == 'B99999999'
        assert company.status == 'active'

    def test_tax_id_unique(self):
        CompanyFactory(tax_id='B11111111')
        with pytest.raises(IntegrityError):
            CompanyFactory(tax_id='B11111111')

    def test_str_trade_name(self):
        company = CompanyFactory(legal_name='Corp Legal', trade_name='Trade')
        assert str(company) == 'Trade'

    def test_str_fallback_to_legal_name(self):
        company = CompanyFactory(trade_name='')
        assert str(company) == company.legal_name

    def test_ordering(self):
        c2 = CompanyFactory(legal_name='Zebra Corp')
        c1 = CompanyFactory(legal_name='Alpha Corp')
        companies = list(Company.objects.all())
        assert companies[0].legal_name == 'Alpha Corp'
        assert companies[1].legal_name == 'Zebra Corp'

    def test_status_choices(self):
        for status in ['active', 'inactive', 'prospect']:
            company = CompanyFactory(status=status)
            assert company.status == status

    def test_optional_fields(self):
        company = CompanyFactory(
            website='https://test.com',
            cnae='5610',
            autonomous_community='Madrid',
        )
        assert company.website == 'https://test.com'
        assert company.cnae == '5610'


@pytest.mark.django_db
class TestCompanyMembership:
    def test_create_membership(self):
        user = UserFactory()
        company = CompanyFactory()
        membership = CompanyMembershipFactory(user=user, company=company)
        assert membership.user == user
        assert membership.company == company
        assert membership.is_active is True

    def test_unique_user_company(self):
        user = UserFactory()
        company = CompanyFactory()
        CompanyMembershipFactory(user=user, company=company)
        with pytest.raises(ValidationError):
            CompanyMembershipFactory(user=user, company=company)

    def test_role_choices(self):
        for role in CompanyMembership.Role:
            membership = CompanyMembershipFactory(role=role)
            assert membership.role == role

    def test_is_default_membership(self):
        user = UserFactory()
        company = CompanyFactory()
        membership = CompanyMembershipFactory(
            user=user, company=company, is_default=True
        )
        assert membership.is_default is True

    def test_only_one_default_per_user(self):
        user = UserFactory()
        c1 = CompanyFactory()
        c2 = CompanyFactory()
        CompanyMembershipFactory(user=user, company=c1, is_default=True, is_active=True)
        with pytest.raises(ValidationError):
            CompanyMembershipFactory(user=user, company=c2, is_default=True, is_active=True)

    def test_membership_str(self):
        membership = CompanyMembershipFactory()
        assert membership.company.legal_name in str(membership) or str(membership.user) in str(membership)
