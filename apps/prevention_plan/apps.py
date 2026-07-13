from django.apps import AppConfig


class PreventionPlanConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.prevention_plan'
    verbose_name = 'Plan de Prevencion'

    def ready(self):
        import apps.prevention_plan.signals  # noqa
