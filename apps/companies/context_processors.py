from apps.companies.models import Company, CompanyMembership


def active_company(request):
    available_companies = Company.objects.none()

    if request.user.is_authenticated:
        if request.user.is_superuser:
            available_companies = Company.objects.filter(
                status=Company.Status.ACTIVE
            ).order_by('legal_name')
        else:
            company_ids = CompanyMembership.objects.filter(
                user=request.user,
                is_active=True,
                company__status=Company.Status.ACTIVE
            ).values_list('company_id', flat=True)

            available_companies = Company.objects.filter(
                id__in=company_ids
            ).order_by('legal_name')

    return {
        'active_company': getattr(request, 'active_company', None),
        'company_membership': getattr(request, 'company_membership', None),
        'available_companies': available_companies,
    }