from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Pobla el catalogo de EPIs del mercado con EPIs comunes'

    def handle(self, *args, **options):
        from apps.epis.models import CatalogoEPI

        epios = [
            {
                'nombre': 'Gafas de proteccion',
                'categoria': 'ojos',
                'riesgos_proteccion': 'Proyecciones de particulas, polvo, salpicaduras',
                'norma_eu': 'EN 166',
                'descripcion': 'Gafas de proteccion general contra impactos leves, polvo y salpicaduras.',
            },
            {
                'nombre': 'Gafas de proteccion con pantalla facial',
                'categoria': 'ojos',
                'riesgos_proteccion': 'Impacto de particulas, salpicaduras quimicas, radiacion UV',
                'norma_eu': 'EN 166 + EN 170',
                'descripcion': 'Gafas con pantalla facial completa para proteccion ocular y facial.',
            },
            {
                'nombre': 'Guantes de proteccion contra cortes',
                'categoria': 'manos',
                'riesgos_proteccion': 'Cortes, rasgados, abrasion',
                'norma_eu': 'EN 388',
                'descripcion': 'Guantes resistentes a cortes para manipulacion de materiales afilados.',
            },
            {
                'nombre': 'Guantes de nitrilo',
                'categoria': 'manos',
                'riesgos_proteccion': 'Quimicos, agentes biologicos, contaminacion',
                'norma_eu': 'EN 374',
                'descripcion': 'Guantes de proteccion contra productos quimicos y agentes biologicos.',
            },
            {
                'nombre': 'Guantes termicos',
                'categoria': 'manos',
                'riesgos_proteccion': 'Frio, conduccion termica, congelacion',
                'norma_eu': 'EN 511',
                'descripcion': 'Guantes aislantes para trabajos en ambiente frio.',
            },
            {
                'nombre': 'Guantes contra vibraciones',
                'categoria': 'manos',
                'riesgos_proteccion': 'Vibraciones de herramientas manuales, impactos',
                'norma_eu': 'EN ISO 10819',
                'descripcion': 'Guantes amortiguadores para uso de herramientas vibratorias.',
            },
            {
                'nombre': 'Calzado de seguridad',
                'categoria': 'pies',
                'riesgos_proteccion': 'Impacto, compresion, punctura, caida de objetos',
                'norma_eu': 'EN ISO 20345',
                'descripcion': 'Calzado con puntera de seguridad que resiste impactos de hasta 200J.',
            },
            {
                'nombre': 'Calzado de proteccion',
                'categoria': 'pies',
                'riesgos_proteccion': 'Impacto, calor, corriente electrica, resbalones',
                'norma_eu': 'EN ISO 20346',
                'descripcion': 'Calzado con proteccion frente a riesgos menos severos que el de seguridad.',
            },
            {
                'nombre': 'Calzado dieléctrico',
                'categoria': 'pies',
                'riesgos_proteccion': 'Corriente electrica, descargas electricas',
                'norma_eu': 'EN 50321',
                'descripcion': 'Calzado aislante para trabajos con riesgo electrico.',
            },
            {
                'nombre': 'Casco de seguridad industrial',
                'categoria': 'cabeza',
                'riesgos_proteccion': 'Caida de objetos, impactos laterales, perforacion',
                'norma_eu': 'EN 397',
                'descripcion': 'Casco protector para trabajos en obras y zonas industriales.',
            },
            {
                'nombre': 'Cascete de proteccion',
                'categoria': 'cabeza',
                'riesgos_proteccion': 'Golpes, impactos leves, caidas accidentales',
                'norma_eu': 'EN 812',
                'descripcion': 'Cascete ligero sin barbilla, para golpes accidentales.',
            },
            {
                'nombre': 'Proteccion auditiva - tapones',
                'categoria': 'oidos',
                'riesgos_proteccion': 'Ruido excesivo, danos auditivos',
                'norma_eu': 'EN 352-2',
                'descripcion': 'Tapones auriculares con atenuacion de ruido para entornos ruidosos.',
            },
            {
                'nombre': 'Proteccion auditiva - orejeras',
                'categoria': 'oidos',
                'riesgos_proteccion': 'Ruido ambiental, danos auditivos',
                'norma_eu': 'EN 352-1',
                'descripcion': 'Orejeras de amortiguacion para proteccion contra ruido.',
            },
            {
                'nombre': 'Mascarilla FFP2',
                'categoria': 'respiratoria',
                'riesgos_proteccion': 'Particulas, polvo, aerosoles no aceitosos',
                'norma_eu': 'EN 149',
                'descripcion': 'Mascarilla filtrante de semifiltro contra particulas solidas y liquidos no aceitosos.',
            },
            {
                'nombre': 'Mascarilla FFP3',
                'categoria': 'respiratoria',
                'riesgos_proteccion': 'Particulas finas, fibras, agentes biologicos, fibra de asbesto',
                'norma_eu': 'EN 149',
                'descripcion': 'Mascarilla filtrante de alta eficiencia contra particulas finas y toxicas.',
            },
            {
                'nombre': 'Respirador semimascarilla',
                'categoria': 'respiratoria',
                'riesgos_proteccion': 'Gases, vapores, partículas组合adas',
                'norma_eu': 'EN 140 + EN 143',
                'descripcion': 'Respirador reutilizable con filtros intercambiables para gases y particulas.',
            },
            {
                'nombre': 'Traje de proteccion quimica',
                'categoria': 'corporal',
                'riesgos_proteccion': 'Quimicos, agentes biologicos, salpicaduras',
                'norma_eu': 'EN 14605',
                'descripcion': 'Traje completo de proteccion contra sustancias quimicas liquidas.',
            },
            {
                'nombre': 'Chaleco de alta visibilidad',
                'categoria': 'corporal',
                'riesgos_proteccion': 'Visibilidad reducida, atropello, accidentes de trafico',
                'norma_eu': 'EN ISO 20471',
                'descripcion': 'Prenda de alta visibilidad para trabajos via carretera y zonas de riesgo.',
            },
            {
                'nombre': 'Traje de proteccion contra lluvia',
                'categoria': 'corporal',
                'riesgos_proteccion': 'Agua, viento, condicion meteorologica adversa',
                'norma_eu': 'EN 343',
                'descripcion': 'Traje impermeable para proteccion frente a lluvia y viento.',
            },
            {
                'nombre': 'Mascara facial completa',
                'categoria': 'respiratoria',
                'riesgos_proteccion': 'Gases toxicos, vapores, ausencia de oxigeno',
                'norma_eu': 'EN 136 + EN 140',
                'descripcion': 'Mascara de cara completa para uso con equipos de respiracion autonoma.',
            },
            {
                'nombre': 'Proteccion facial transparente',
                'categoria': 'ojos',
                'riesgos_proteccion': 'Salpicaduras quimicas, proyeccion de particulas, chispas',
                'norma_eu': 'EN 166',
                'descripcion': 'Pantalla facial de policarbonato para proteccion completa del rostro.',
            },
            {
                'nombre': 'Mandil de proteccion',
                'categoria': 'corporal',
                'riesgos_proteccion': 'Salpicaduras, chispas, calor radiante',
                'norma_eu': 'EN 11611 / EN 11612',
                'descripcion': 'Mandil resistente a llama y calor para soldadura y corte.',
            },
            {
                'nombre': 'Guantes de soldador',
                'categoria': 'manos',
                'riesgos_proteccion': 'Calor, chispas, salpicaduras de metal fundido',
                'norma_eu': 'EN 12477',
                'descripcion': 'Guantes de cuero para proteccion durante operaciones de soldadura.',
            },
            {
                'nombre': 'Manguitos de proteccion',
                'categoria': 'manos',
                'riesgos_proteccion': 'Calor, abrasion, cortes leves en antebrazos',
                'norma_eu': 'EN 388',
                'descripcion': 'Manguitos protectores para antebrazos en tareas industriales.',
            },
        ]

        creados = 0
        for datos in epios:
            obj, created = CatalogoEPI.objects.get_or_create(
                nombre=datos['nombre'],
                defaults=datos,
            )
            if created:
                creados += 1
                self.stdout.write(f'  + {obj}')

        self.stdout.write(self.style.SUCCESS(
            f'Catalogo actualizado: {creados} creados, {len(epios) - creados} ya existian.'
        ))
