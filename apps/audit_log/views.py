from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView

from apps.audit_log.models import AuditLog


class AuditLogListView(LoginRequiredMixin, ListView):
    model = AuditLog
    template_name = 'audit_log/log_list.html'
    context_object_name = 'logs'
    paginate_by = 50
    ordering = ['-timestamp']

    def get_queryset(self):
        qs = super().get_queryset().select_related('user', 'empresa')

        empresa = getattr(self.request, 'active_company', None)
        if empresa and not self.request.user.is_superuser:
            qs = qs.filter(empresa=empresa)

        action = self.request.GET.get('action')
        if action:
            qs = qs.filter(action=action)

        model_name = self.request.GET.get('model')
        if model_name:
            qs = qs.filter(model_name=model_name)

        origin = self.request.GET.get('origin')
        if origin:
            qs = qs.filter(origin=origin)

        user_id = self.request.GET.get('user')
        if user_id:
            qs = qs.filter(user_id=user_id)

        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(object_repr__icontains=q)

        return qs


class AuditLogDetailView(LoginRequiredMixin, DetailView):
    model = AuditLog
    template_name = 'audit_log/log_detail.html'
    context_object_name = 'log'
