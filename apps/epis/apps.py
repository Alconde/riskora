from django.apps import AppConfig


class EpisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.epis'
    verbose_name = 'EPIs'

    def ready(self):
        import apps.epis.signals  # noqa: F401
