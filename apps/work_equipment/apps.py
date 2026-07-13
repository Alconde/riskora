from django.apps import AppConfig


class WorkEquipmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.work_equipment'
    verbose_name = 'Equipos de trabajo'

    def ready(self):
        import apps.work_equipment.signals  # noqa: F401
