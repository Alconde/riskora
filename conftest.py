import pytest
from django.test import RequestFactory
from apps.accounts.models import User
from apps.companies.models import Company, CompanyMembership


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User',
        role=User.Role.TECHNICIAN,
    )


@pytest.fixture
def superuser(db):
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
        first_name='Admin',
        last_name='Super',
    )


@pytest.fixture
def company(db):
    return Company.objects.create(
        legal_name='Empresa Test S.L.',
        trade_name='Empresa Test',
        tax_id='B12345678',
        email='info@empresatest.com',
        phone='912345678',
        address='Calle Mayor 1',
        postal_code='28001',
        city='Madrid',
        province='Madrid',
        activity='Hostelería',
        workforce_size=50,
    )


@pytest.fixture
def company2(db):
    return Company.objects.create(
        legal_name='Segunda Empresa S.A.',
        trade_name='Segunda Empresa',
        tax_id='A87654321',
        email='info@segunda.com',
    )


@pytest.fixture
def membership(db, user, company):
    return CompanyMembership.objects.create(
        user=user,
        company=company,
        role=CompanyMembership.Role.COMPANY_ADMIN,
        is_active=True,
        is_default=True,
    )


@pytest.fixture
def auth_client(client, user, membership):
    client.login(username='testuser', password='testpass123')
    return client


@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.fixture
def company_request(request_factory, user, company):
    request = request_factory.get('/')
    request.user = user
    request.session = {}
    request.active_company = company
    request.company_membership = CompanyMembership.objects.filter(
        user=user, company=company
    ).first()
    return request


@pytest.fixture
def superuser_request(request_factory, superuser, company):
    request = request_factory.get('/')
    request.user = superuser
    request.session = {'active_company_id': company.pk}
    request.active_company = company
    request.company_membership = None
    return request
