from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils import timezone


# ---------------------------------------------------------------------------
# Mixins de Modelo
# ---------------------------------------------------------------------------

class AuditFieldsMixin(models.Model):
    """
    Mixin abstracto que añade campos de auditoría a cualquier modelo.
    created_at / updated_at se gestionan con auto_now / auto_now_add.
    created_by / updated_by se rellenan desde la vista o el signal.
    """

    created_at = models.DateTimeField('creado el', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado el', auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        verbose_name='creado por',
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        verbose_name='actualizado por',
    )

    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    """Devuelve solo registros no eliminados lógicamente."""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteMixin(models.Model):
    """
    Mixin abstracto para borrado lógico.
    Solo se debe usar en modelos donde el borrado físico no es conveniente.
    """

    deleted_at = models.DateTimeField('eliminado el', null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_deleted',
        verbose_name='eliminado por',
    )
    is_deleted = models.BooleanField('eliminado', default=False, db_index=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, **kwargs):
        self.deleted_at = timezone.now()
        self.is_deleted = True
        self.save(using=using)

    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self, using=None):
        self.deleted_at = None
        self.is_deleted = False
        self.save(using=using)


# ---------------------------------------------------------------------------
# Mixins de Vista
# ---------------------------------------------------------------------------

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
        active_company = self.get_active_company_or_none()

        if active_company:
            return queryset.filter(
                **self.get_company_filter_kwargs(active_company)
            )

        if self.is_global_access_allowed():
            return queryset

        return queryset.none()

    def get_company_scoped_queryset(self, queryset=None):
        queryset = queryset if queryset is not None else self.get_base_queryset()
        return self.scope_queryset_to_company(queryset)