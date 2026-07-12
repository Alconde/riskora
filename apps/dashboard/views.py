from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.core.mixins import CompanyScopedMixin
from apps.dashboard.services import build_dashboard_context


class DashboardView(LoginRequiredMixin, CompanyScopedMixin, TemplateView):
    template_name = 'dashboard/home.html'
    login_url = '/login/'
    company_field_name = 'company'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_company = self.get_active_company()
        is_superuser = self.request.user.is_superuser

        context.update(
            build_dashboard_context(
                active_company=active_company,
                is_superuser=is_superuser
            )
        )
        return context