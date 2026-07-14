from django.core.management.base import BaseCommand
from apps.audits.services import CHECKLIST_ISO_45001


class Command(BaseCommand):
    help = 'Muestra la plantilla de checklist ISO 45001:2018 disponible en audits.services'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                f'Plantilla ISO 45001 — {len(CHECKLIST_ISO_45001)} cláusulas cargadas:'
            )
        )
        self.stdout.write('')
        for item in CHECKLIST_ISO_45001:
            self.stdout.write(
                f"  [{item['id']:02d}] {item['clausula']:8s} — {item['requisito']}"
            )
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                'La plantilla está disponible vía services.get_checklist_plantilla().'
            )
        )
        self.stdout.write(
            'Para pre-cargar en una auditoría, use la vista de carga masiva (checklist_bulk).'
        )
