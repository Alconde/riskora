from datetime import date

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.legal_requirements.models import NormativaLegal, RequisitoLegal
from apps.legal_requirements.services import NORMATIVA_PRL_ESPANOLA, get_requisitos_por_categoria


def parse_date(date_str):
    if not date_str:
        return None
    parts = date_str.split('-')
    return date(int(parts[0]), int(parts[1]), int(parts[2]))


# Mapping normativa numero -> categorías de requisitos a crear
NORMATIVA_CATEGORIAS = {
    '31/1995': ['prevencion', 'formacion', 'documentacion'],
    '39/1997': ['prevencion', 'formacion', 'instalaciones'],
    '486/1997': ['instalaciones'],
    '140/2003': ['instalaciones'],
    '2177/2004': ['instalaciones', 'emergencias'],
    '156/2010': ['instalaciones'],
    '1215/1997': ['epis', 'instalaciones'],
    '116/2002': ['epis', 'instalaciones'],
    '664/1997': ['vigilancia', 'epis'],
    '374/2001': ['vigilancia', 'epis'],
    '1027/2007': ['instalaciones'],
    '614/2001': ['instalaciones'],
    '84/2015': ['epis'],
    '604/2004': ['instalaciones'],
    '773/1997': ['emergencias'],
    '1620/1997': ['vigilancia'],
    '513/2017': ['vigilancia', 'epis'],
    '335/2002': ['notificacion'],
}


class Command(BaseCommand):
    help = 'Carga la normativa PRL española básica en la base de datos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Borrar toda la normativa existente antes de cargar',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Borrando normativa existente...'))
            NormativaLegal.objects.all().delete()

        created_count = 0
        skipped_count = 0

        for norm in NORMATIVA_PRL_ESPANOLA:
            obj, created = NormativaLegal.objects.get_or_create(
                numero=norm['numero'],
                defaults={
                    'nombre': norm['nombre'],
                    'tipo': norm['tipo'],
                    'ambito': norm['ambito'],
                    'fecha_publicacion': parse_date(norm['fecha_publicacion']),
                    'fecha_vigencia': parse_date(norm.get('fecha_vigencia')),
                    'resumen': norm.get('resumen', ''),
                    'activa': True,
                },
            )
            if created:
                created_count += 1
                self.stdout.write(f'  [+] {obj}')
            else:
                skipped_count += 1
                self.stdout.write(f'  [=] Ya existe: {obj}')

        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                f'Normativa: {created_count} creada(s), {skipped_count} existente(s)'
            )
        )

        # Cargar requisitos tipicos por cada normativa
        req_created = 0
        normativas = NormativaLegal.objects.filter(activa=True)
        for norm in normativas:
            categorias = NORMATIVA_CATEGORIAS.get(norm.numero, [])
            for cat in categorias:
                requisitos = get_requisitos_por_categoria(cat)
                for req_texto in requisitos:
                    _, created = RequisitoLegal.objects.get_or_create(
                        normativa=norm,
                        titulo=req_texto,
                        defaults={
                            'descripcion': f'Obligación derivada de {norm}. {req_texto}',
                            'categoria': cat,
                        },
                    )
                    if created:
                        req_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Requisitos: {req_created} creados'
            )
        )
