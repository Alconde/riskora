import pytest
from django.db import IntegrityError
from apps.accounts.models import User
from tests.factories import UserFactory, SuperUserFactory


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = UserFactory(username='juan', email='juan@test.com')
        assert user.username == 'juan'
        assert user.email == 'juan@test.com'
        assert user.role == User.Role.TECHNICIAN
        assert user.is_active is True
        assert user.check_password('testpass123')

    def test_create_superuser(self):
        user = SuperUserFactory(username='admin1')
        assert user.is_superuser is True
        assert user.is_staff is True
        assert user.check_password('adminpass123')

    def test_email_unique(self):
        UserFactory(email='unique@test.com')
        with pytest.raises(IntegrityError):
            UserFactory(email='unique@test.com')

    def test_username_unique(self):
        UserFactory(username='uniqueuser')
        with pytest.raises(IntegrityError):
            UserFactory(username='uniqueuser')

    def test_role_default(self):
        user = User.objects.create_user(
            username='defaultrole', email='default@test.com', password='pass'
        )
        assert user.role == User.Role.VIEWER

    def test_role_choices(self):
        for role in User.Role:
            user = UserFactory(role=role)
            assert user.role == role

    def test_str_representation(self):
        user = UserFactory(first_name='María', last_name='García')
        assert str(user) == 'María García'

    def test_str_fallback_to_username(self):
        user = UserFactory(first_name='', last_name='', username='fallbackuser')
        assert str(user) == 'fallbackuser'

    def test_optional_fields(self):
        user = UserFactory(phone='612345678', job_title='Téc. Prevención')
        assert user.phone == '612345678'
        assert user.job_title == 'Téc. Prevención'

    def test_is_verified_default_false(self):
        user = UserFactory()
        assert user.is_verified is False
