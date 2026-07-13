from django.core.management.base import BaseCommand
from apps.emergency_measures.models import MedioProteccionIncendios
from apps.training.models import TrainingCategory


MEDIOS_DEFAULT = [
    {'nombre': 'Extintor de Polvo', 'descripcion': 'Extintor de polvo ABC, 6/8 kg. Uso general contra fuegos de clase A, B y C.'},
    {'nombre': 'Extintor de CO2', 'descripcion': 'Extintor de dioxido de carbono, 5/10 kg. Ideal para riesgos electricos y fuegos de clase B.'},
    {'nombre': 'BIE 25 (Boquilla Intermedia)', 'descripcion': 'Boquilla de interpconexion 25mm, 20m de manguera.'},
    {'nombre': 'BIE 45 (Boquilla Intermedia)', 'descripcion': 'Boquilla de interpconexion 45mm, 20/30m de manguera.'},
    {'nombre': 'Iluminacion de Emergencia', 'descripcion': 'Luminarias de emergencia con autonomia minima de 1 hora.'},
    {'nombre': 'Botiquin de Primeros Auxilios', 'descripcion': 'Botiquin normalizado con material de cura y primeros auxilios.'},
    {'nombre': 'Alarma de Emergencia', 'descripcion': 'Sistema de alarma sonora para emergencias.'},
    {'nombre': 'Sirena de Emergencia', 'descripcion': 'Sirena manual o automatica para evacuacion.'},
    {'nombre': 'Pulsador de Alarma', 'descripcion': 'Pulsador manual conectado al sistema de alarma.'},
    {'nombre': 'Manta Ignifuga', 'descripcion': 'Manta contra fuegos para extincion inicial o proteccion personal.'},
    {'nombre': 'Retenedor de Manguera', 'descripcion': 'Retenedor para manguera de BIE.'},
    {'nombre': 'Salida de Emergencia (señalizacion)', 'descripcion': 'Señalizacion fotoluminiscente de salidas de emergencia.'},
    {'nombre': 'Señalizacion de Ruta de Evacuacion', 'descripcion': 'Señales de direccion de evacuacion fotoluminiscentes.'},
    {'nombre': 'Punto de Reunion', 'descripcion': 'Señalizacion del punto de reunion exterior.'},
    {'nombre': 'Chorro de Arena', 'descripcion': 'Equipo de extension fija con boquilla de arena para riesgos especificos.'},
    {'nombre': 'Hidrante Exterior', 'descripcion': 'Hidrante de columna de incendios equipada (CIE).'},
    {'nombre': 'Pulsera Luminiscente', 'descripcion': 'Pulsera de seguridad fotoluminiscente para el equipo de emergencia.'},
    {'nombre': 'Megafono', 'descripcion': 'Megafono portatil para comunicaciones de emergencia.'},
    {'nombre': 'Cinta de balizamiento', 'descripcion': 'Cinta de precintado para balizar zonas de peligro.'},
    {'nombre': 'Guantes ignifugos', 'descripcion': 'Guantes de proteccion termica para el equipo de intervencion.'},
]

CATEGORIAS_EMERGENCIA = [
    {'name': 'Prevencion de Incendios', 'code': 'INCENDIOS', 'description': 'Formacion en prevencion y extincion de incendios.'},
    {'name': 'Primeros Auxilios', 'code': 'AUXILIOS', 'description': 'Formacion en primeros auxilios y RCP.'},
    {'name': 'Medidas de Emergencia', 'code': 'EMERGENCIAS', 'description': 'Formacion sobre protocolos y medidas de emergencia.'},
    {'name': 'Evacuacion', 'code': 'EVACUACION', 'description': 'Formacion en procedimientos de evacuacion.'},
    {'name': 'Uso de Extintores', 'code': 'EXTINTORES', 'description': 'Formacion practica en el uso de extintores.'},
]


class Command(BaseCommand):
    help = 'Seed catalogo de medios de proteccion y categorias de formacion de emergencia'

    def handle(self, *args, **options):
        count_medios = 0
        for m in MEDIOS_DEFAULT:
            _, created = MedioProteccionIncendios.objects.get_or_create(
                nombre=m['nombre'],
                defaults={'descripcion': m['descripcion']},
            )
            if created:
                count_medios += 1

        count_cats = 0
        for c in CATEGORIAS_EMERGENCIA:
            _, created = TrainingCategory.objects.get_or_create(
                code=c['code'],
                defaults={'name': c['name'], 'description': c['description']},
            )
            if created:
                count_cats += 1

        self.stdout.write(self.style.SUCCESS(
            f'Creados {count_medios} medios de proteccion y {count_cats} categorias de formacion.'
        ))
