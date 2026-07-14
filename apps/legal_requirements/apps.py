from django.apps import AppConfig


class LegalRequirementsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.legal_requirements'
    verbose_name = 'Requisitos Legales'

    def ready(self):
        import apps.legal_requirements.signals  # noqa: F401
