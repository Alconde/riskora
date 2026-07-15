import uuid
from threading import local

from django.db import models

_thread_locals = local()


class AuditService:
    """
    Punto único de entrada para el registro de auditoría.

    Uso:
        from apps.audit_log.services import AuditService

        # Para operaciones CRUD (llamado desde signals):
        AuditService.log_crud(instance, 'create')

        # Para procesos de negocio:
        AuditService.log(
            action='export',
            model_name='EvaluacionRiesgos',
            object_id=evaluacion.pk,
            object_repr=str(evaluacion),
            origin='IMPORT',
            empresa=empresa,
            user=user,
        )
    """

    @classmethod
    def set_current_request(cls, request):
        _thread_locals.current_request = request

    @classmethod
    def get_current_request(cls):
        return getattr(_thread_locals, 'current_request', None)

    @classmethod
    def clear_current_request(cls):
        _thread_locals.current_request = None

    @classmethod
    def log(
        cls,
        *,
        action: str,
        model_name: str,
        object_id=None,
        object_repr: str = '',
        changes: dict | None = None,
        user=None,
        empresa=None,
        origin: str = 'USER',
        request=None,
        parent_event_id: uuid.UUID | None = None,
        trace_id: uuid.UUID | None = None,
    ):
        from apps.audit_log.models import AuditLog

        request = request or cls.get_current_request()

        if user is None and request and hasattr(request, 'user'):
            user = request.user if request.user.is_authenticated else None

        if empresa is None and request and hasattr(request, 'active_company'):
            empresa = request.active_company

        ip_address = None
        user_agent = ''
        if request:
            ip_address = cls._get_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

        if trace_id is None and request and hasattr(request, 'audit_trace_id'):
            trace_id = request.audit_trace_id
        if trace_id is None:
            trace_id = uuid.uuid4()

        request_id = None
        if request and hasattr(request, 'audit_request_id'):
            request_id = request.audit_request_id
        if request_id is None:
            request_id = uuid.uuid4()

        AuditLog.objects.create(
            request_id=request_id,
            trace_id=trace_id,
            parent_event_id=parent_event_id,
            user=user,
            empresa=empresa,
            origin=origin,
            ip_address=ip_address,
            user_agent=user_agent,
            action=action,
            model_name=model_name,
            object_id=str(object_id) if object_id else '',
            object_repr=str(object_repr)[:300] if object_repr else '',
            changes=changes or {},
        )

    @classmethod
    def log_crud(cls, instance, action: str, user=None, request=None, **kwargs):
        changes = {}
        if action == 'update' and hasattr(instance, '_audit_changes'):
            changes = instance._audit_changes

        cls.log(
            action=action,
            model_name=instance.__class__.__name__,
            object_id=instance.pk,
            object_repr=str(instance)[:300],
            changes=changes,
            user=user,
            request=request,
            **kwargs,
        )

    @classmethod
    def _get_ip(cls, request) -> str | None:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
