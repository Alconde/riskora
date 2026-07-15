from django.db import migrations


REQUISITOS = [
    # ── Equipos de trabajo ──
    {
        'nombre': 'Carretilla elevadora',
        'tipo': 'equipo',
        'categoria': 'Maquinaria',
        'normativa': 'RD 1215/1997',
        'descripcion': 'Operación de carretillas elevadoras industriales. Formación obligatoria según normativa de equipos de trabajo.',
    },
    {
        'nombre': 'Plataforma elevadora (plumier)',
        'tipo': 'equipo',
        'categoria': 'Maquinaria',
        'normativa': 'RD 995/2009',
        'descripcion': 'Operación de plataformas elevadoras de personal (plumiers).',
    },
    {
        'nombre': 'Grúa puente / puente grúa',
        'tipo': 'equipo',
        'categoria': 'Maquinaria',
        'normativa': 'RD 809/2015, RD 1215/1997',
        'descripcion': 'Operación de grúas puente y puentes grúa. Acreditación de organismos autorizados.',
    },
    {
        'nombre': 'Montacargas / apiladores',
        'tipo': 'equipo',
        'categoria': 'Maquinaria',
        'normativa': 'RD 1215/1997',
        'descripcion': 'Operación de montacargas, apiladores y transpaletas motorizadas.',
    },
    {
        'nombre': 'Soldadura (autógena / eléctrica / MIG-MAG / TIG)',
        'tipo': 'equipo',
        'categoria': 'Maquinaria',
        'normativa': 'RD 1215/1997',
        'descripcion': 'Operación de equipos de soldadura y corte. Certificación según UNE-EN ISO 9606.',
    },
    {
        'nombre': 'Herramienta neumática',
        'tipo': 'equipo',
        'categoria': 'Herramientas',
        'normativa': 'RD 1215/1997',
        'descripcion': 'Uso de herramientas neumáticas (mazos, destornilladores, amoladoras).',
    },
    {
        'nombre': 'Equipo de elevación (eslingas, ganchos, grilletes)',
        'tipo': 'equipo',
        'categoria': 'Maquinaria',
        'normativa': 'RD 809/2015',
        'descripcion': 'Manejo de eslingas, ganchos, grilletes y demás aparejos de elevación.',
    },
    {
        'nombre': 'Vehículos industriales',
        'tipo': 'equipo',
        'categoria': 'Vehículos',
        'normativa': 'Ley 6/2003, RD 1098/2009',
        'descripcion': 'Conducción de vehículos industriales dentro del centro de trabajo.',
    },

    # ── Trabajos / Actividades ──
    {
        'nombre': 'Trabajo en altura',
        'tipo': 'trabajo',
        'categoria': 'Trabajos especiales',
        'normativa': 'RD 2177/2004',
        'descripcion': 'Trabajo a más de 2 metros de altura con riesgo de caída. Uso de arneses, líneas de vida, andamios.',
    },
    {
        'nombre': 'Recintos confinados',
        'tipo': 'trabajo',
        'categoria': 'Trabajos especiales',
        'normativa': 'RD 134/2004',
        'descripcion': 'Trabajo en espacios confinados: tanques, depósitos, pozos, conductos. Plan de rescate obligatorio.',
    },
    {
        'nombre': 'Trabajo con amianto',
        'tipo': 'trabajo',
        'categoria': 'Trabajos especiales',
        'normativa': 'RD 374/2001',
        'descripcion': 'Manipulación de materiales que contienen amianto. Formación y reconocimiento médico específico.',
    },
    {
        'nombre': 'Permitido de trabajo (PT)',
        'tipo': 'trabajo',
        'categoria': 'Trabajos especiales',
        'normativa': 'Art. 24 Ley 31/1995',
        'descripcion': 'Emisión y gestión de permitos de trabajo para actividades de riesgo.',
    },
    {
        'nombre': 'Electricidad (baja y alta tensión)',
        'tipo': 'trabajo',
        'categoria': 'Trabajos especiales',
        'normativa': 'RD 614/2001, Reglamento Electrotécnico BT',
        'descripcion': 'Trabajos en instalaciones eléctricas. Autorización según nivel de tensión.',
    },
    {
        'nombre': 'Maniobras de carga y descarga',
        'tipo': 'trabajo',
        'categoria': 'Operaciones especiales',
        'normativa': 'RD 1215/1997',
        'descripcion': 'Operaciones de carga, descarga y estiba de mercancías con riesgo.',
    },
    {
        'nombre': 'Uso de EPIs de protección colectiva',
        'tipo': 'trabajo',
        'categoria': 'Protección colectiva',
        'normativa': 'RD 186/2008',
        'descripcion': 'Instalación y manejo de equipos de protección colectiva: barandillas, redes, plataformas.',
    },
    {
        'nombre': 'Primeros auxilios y RCP',
        'tipo': 'trabajo',
        'categoria': 'Emergencias',
        'normativa': 'Art. 19 Ley 31/1995',
        'descripcion': 'Formación en primeros auxilios y reanimación cardiopulmonar (RCP).',
    },
]


def forwards(apps, schema_editor):
    RequisitoAutorizacion = apps.get_model('authorizations', 'RequisitoAutorizacion')
    for r in REQUISITOS:
        RequisitoAutorizacion.objects.get_or_create(
            nombre=r['nombre'],
            empresa_id=None,
            defaults={
                'tipo': r['tipo'],
                'categoria': r['categoria'],
                'normativa': r['normativa'],
                'descripcion': r['descripcion'],
            },
        )


def backwards(apps, schema_editor):
    RequisitoAutorizacion = apps.get_model('authorizations', 'RequisitoAutorizacion')
    RequisitoAutorizacion.objects.filter(empresa_id__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('authorizations', '0001_initial_models'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
