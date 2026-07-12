from django.core.management.base import BaseCommand
from apps.training.models import TrainingRecord
from apps.training.services import refresh_training_alerts_for_record


class Command(BaseCommand):
    help = 'Actualiza alertas y estados operativos del módulo training'

    def handle(self, *args, **options):
        total = 0
        for record in TrainingRecord.objects.select_related('company', 'worker', 'course'):
            refresh_training_alerts_for_record(record)
            total += 1

        self.stdout.write(self.style.SUCCESS(f'Revisados {total} registros de formación'))