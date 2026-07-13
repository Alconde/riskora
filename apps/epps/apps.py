from django.apps import AppConfig


class EppsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.epps'
    verbose_name = 'Enfermedades Profesionales'

    def ready(self):
        import apps.epps.signals  # noqa: F401
