import pytest
from apps.tasks.models import Task, Alert
from tests.factories import CompanyFactory, TaskFactory, AlertFactory


@pytest.mark.django_db
class TestTask:
    def test_create_task(self):
        task = TaskFactory(
            title='Revisar EPIs',
            status='pending',
            priority='high',
        )
        assert task.title == 'Revisar EPIs'
        assert task.status == 'pending'
        assert task.priority == 'high'

    def test_status_choices(self):
        for status in ['pending', 'in_progress', 'completed', 'cancelled']:
            task = TaskFactory(status=status)
            assert task.status == status

    def test_priority_choices(self):
        for priority in ['low', 'medium', 'high', 'critical']:
            task = TaskFactory(priority=priority)
            assert task.priority == priority

    def test_str_representation(self):
        task = TaskFactory(title='Tarea Test')
        assert str(task) == 'Tarea Test'


@pytest.mark.django_db
class TestAlert:
    def test_create_alert(self):
        alert = AlertFactory(
            title='Vencimiento documento',
            alert_type='document_expiry',
            severity='warning',
        )
        assert alert.title == 'Vencimiento documento'
        assert alert.alert_type == 'document_expiry'
        assert alert.severity == 'warning'
        assert alert.is_active is True
        assert alert.is_read is False

    def test_alert_type_choices(self):
        for at in ['document_expiry', 'document_review', 'training_expiry',
                    'health_surveillance', 'generic']:
            alert = AlertFactory(alert_type=at)
            assert alert.alert_type == at

    def test_severity_choices(self):
        for sev in ['info', 'warning', 'danger']:
            alert = AlertFactory(severity=sev)
            assert alert.severity == sev

    def test_str_representation(self):
        alert = AlertFactory(title='Alerta Test')
        assert str(alert) == 'Alerta Test'
