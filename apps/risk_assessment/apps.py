from django.apps import AppConfig


class RiskAssessmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.risk_assessment'
    verbose_name = 'Evaluación de Riesgos'

    def ready(self):
        import apps.risk_assessment.signals  # noqa: F401
