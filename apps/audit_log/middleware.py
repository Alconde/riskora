from apps.audit_log.services import AuditService


class AuditContextMiddleware:
    """
    Middleware que proporciona contexto de auditoría para cada request.
    Genera request_id y trace_id únicos por petición HTTP.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        import uuid

        request.audit_request_id = uuid.uuid4()
        request.audit_trace_id = uuid.uuid4()

        AuditService.set_current_request(request)

        response = self.get_response(request)

        AuditService.clear_current_request()

        return response
