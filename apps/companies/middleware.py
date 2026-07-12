from apps.companies.models import Company, CompanyMembership


class ActiveCompanyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.active_company = None
        request.company_membership = None

        if request.user.is_authenticated:
            if request.user.is_superuser:
                company_id = request.session.get('active_company_id')
                if company_id:
                    request.active_company = Company.objects.filter(pk=company_id).first()
            else:
                memberships = CompanyMembership.objects.select_related('company').filter(
                    user=request.user,
                    is_active=True,
                    company__status=Company.Status.ACTIVE
                )

                company_id = request.session.get('active_company_id')

                if company_id:
                    membership = memberships.filter(company_id=company_id).first()
                    if membership:
                        request.active_company = membership.company
                        request.company_membership = membership

                if request.active_company is None:
                    membership = memberships.filter(is_default=True).first() or memberships.first()
                    if membership:
                        request.active_company = membership.company
                        request.company_membership = membership
                        request.session['active_company_id'] = membership.company_id

        response = self.get_response(request)
        return response