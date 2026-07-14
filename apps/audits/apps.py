from django.apps import AppConfig


class AuditsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.audits'
    verbose_name = 'Auditorías Internas'

    def ready(self):
        import apps.audits.signals  # noqa: F401
