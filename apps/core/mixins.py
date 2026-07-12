from django.core.exceptions import ImproperlyConfigured


class CompanyScopedMixin:
    company_field_name = 'company'
    allow_superuser_global = True

    def get_company_field_name(self):
        if not self.company_field_name:
            raise ImproperlyConfigured(
                f'{self.__class__.__name__} debe definir company_field_name.'
            )
        return self.company_field_name

    def get_active_company(self):
        return getattr(self.request, 'active_company', None)

    def get_active_company_or_none(self):
        return self.get_active_company()

    def is_global_access_allowed(self):
        user = getattr(self.request, 'user', None)
        return bool(
            self.allow_superuser_global and
            user and
            user.is_authenticated and
            user.is_superuser
        )

    def get_base_queryset(self):
        if hasattr(self, 'queryset') and self.queryset is not None:
            return self.queryset.all()

        parent = super()
        if hasattr(parent, 'get_queryset'):
            return parent.get_queryset()

        raise ImproperlyConfigured(
            f'{self.__class__.__name__} debe definir queryset, model o implementar '
            f'get_base_queryset()/get_queryset().'
        )

    def get_company_filter_kwargs(self, active_company):
        return {
            self.get_company_field_name(): active_company
        }

    def scope_queryset_to_company(self, queryset):
        if self.is_global_access_allowed():
            return queryset

        active_company = self.get_active_company_or_none()
        if not active_company:
            return queryset.none()

        return queryset.filter(
            **self.get_company_filter_kwargs(active_company)
        )

    def get_company_scoped_queryset(self, queryset=None):
        queryset = queryset if queryset is not None else self.get_base_queryset()
        return self.scope_queryset_to_company(queryset)