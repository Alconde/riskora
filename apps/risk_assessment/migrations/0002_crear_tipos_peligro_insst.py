from django.db import migrations


TIPOS_PELIGRO_INSST = [
    # Mecánicos
    ('MEC001', 'Rotación', 'mecanico', 'Movimientos de rotación de elementos mecánicos', 'RD 1215/1997'),
    ('MEC002', 'Partes móviles', 'mecanico', 'Contacto con partes móviles de máquinas', 'RD 1215/1997'),
    ('MEC003', 'Elementos a presión', 'mecanico', 'Rotura o proyección de elementos a presión', 'RD 1215/1997'),
    ('MEC004', 'Caída de objetos', 'mecanico', 'Caída de objetos por desplome o caída en altura', 'Ley 31/1995'),
    ('MEC005', 'Proyección de partículas', 'mecanico', 'Proyección de partículas sólidas', 'RD 1215/1997'),

    # Físicos
    ('FIS001', 'Ruido', 'fisico', 'Exposición a niveles de ruido superiores a 80 dB(A)', 'RD 286/2006'),
    ('FIS002', 'Vibraciones', 'fisico', 'Exposición a vibraciones mecánicas', 'RD 1316/1989'),
    ('FIS003', 'Radiaciones ionizantes', 'fisico', 'Exposición a radiaciones ionizantes', 'RD 783/2001'),
    ('FIS004', 'Radiaciones no ionizantes', 'fisico', 'Exposición a radiaciones no ionizantes (láser, UV, IR)', 'RD 1316/1989'),
    ('FIS005', 'Temperaturas extremas', 'fisico', 'Exposición a calor o frío extremo', 'Ley 31/1995'),
    ('FIS006', 'Iluminación deficiente', 'fisico', 'Insuficiente o excesiva iluminación', 'RD 486/1997'),
    ('FIS007', 'Ruido ambiental', 'fisico', 'Ruido producido por fuentes diversas en el puesto', 'RD 286/2006'),

    # Químicos
    ('QUI001', 'Polvos', 'quimico', 'Inhalación de polvos nocivos', 'RD 374/2001'),
    ('QUI002', 'Humos', 'quimico', 'Inhalación de humos industriales', 'RD 374/2001'),
    ('QUI003', 'Nieblas', 'quimico', 'Exposición a nieblas químicas', 'RD 374/2001'),
    ('QUI004', 'Gases', 'quimico', 'Exposición a gases tóxicos o asfixiantes', 'RD 374/2001'),
    ('QUI005', 'Vapores', 'quimico', 'Exposición a vapores químicos', 'RD 374/2001'),
    ('QUI006', 'Líquidos', 'quimico', 'Contacto con líquidos nocivos o corrosivos', 'RD 374/2001'),
    ('QUI007', 'Sólidos', 'quimico', 'Contacto con sustancias sólidas nocivas', 'RD 374/2001'),
    ('QUI008', 'CAE - Cancerígenos', 'quimico', 'Exposición a agentes cancerígenos', 'RD 171/2004'),
    ('QUI009', 'Sensibilizantes', 'quimico', 'Exposición a sustancias sensibilizantes', 'RD 374/2001'),

    # Eléctricos
    ('ELE001', 'Corriente eléctrica', 'electrico', 'Contacto directo o indirecto con instalaciones eléctricas', 'RD 614/2001'),
    ('ELE002', 'Arco eléctrico', 'electrico', 'Riesgo de arco eléctrico por cortocircuito', 'RD 614/2001'),
    ('ELE003', 'Campo electromagnético', 'electrico', 'Exposición a campos electromagnéticos de baja frecuencia', 'RD 316/2006'),

    # Ergonómicos
    ('ERG001', 'Movimientos repetitivos', 'ergonomico', 'Ejecución repetitiva de movimientos con una parte del cuerpo', 'Real Decreto 1004/2017'),
    ('ERG002', 'Posturas forzadas', 'ergonomico', 'Mantenimiento de posturas incómodas o forzadas', 'Real Decreto 1004/2017'),
    ('ERG003', 'Esfuerzo físico', 'ergonomico', 'Manipulación manual de cargas pesadas', 'RD 1004/2017'),
    ('ERG004', 'Pantallas de visualización', 'ergonomico', 'Uso prolongado de pantallas de visualización de datos', 'RD 486/1997'),
    ('ERG005', 'Ritmo de trabajo', 'ergonomico', 'Imposición de ritmos de trabajo inadecuados', 'Ley 31/1995'),

    # Psicosociales
    ('PSI001', 'Estrés laboral', 'psicosocial', 'Situaciones de estrés por carga de trabajo o clima organizacional', 'Ley 31/1995'),
    ('PSI002', 'Violencia', 'psicosocial', 'Riesgo de violencia física o psicológica en el trabajo', 'Ley 31/1995'),
    ('PSI003', 'Acoso laboral (mobbing)', 'psicosocial', 'Situaciones de acoso psicológico en el trabajo', 'Ley 31/1995'),
    ('PSI004', 'Turnicidad', 'psicosocial', 'Jornadas nocturnas o rotación de turnos', 'Ley 31/1995'),
    ('PSI005', 'Fatiga', 'psicosocial', 'Agotamiento físico o mental por condiciones de trabajo', 'Ley 31/1995'),

    # Biológicos
    ('BIO001', 'Agentes biológicos', 'biologico', 'Exposición a agentes biológicos (virus, bacterias, hongos)', 'RD 664/1997'),
    ('BIO002', 'Legionella', 'biologico', 'Riesgo de exposición a Legionella pneumophila', 'RD 865/2003'),
    ('BIO003', 'Materiales biológicos', 'biologico', 'Manipulación de materiales biológicos contaminados', 'RD 664/1997'),

    # Locativos
    ('LOC001', 'Caídas al mismo nivel', 'locativo', 'Resbalones, tropiezos y caídas en superficies de trabajo', 'RD 486/1997'),
    ('LOC002', 'Caídas a distinto nivel', 'locativo', 'Caídas desde altura (andamios, escaleras, tejados)', 'RD 486/1997'),
    ('LOC003', 'Golpes contra objetos', 'locativo', 'Impacto con objetos fijos o móviles', 'Ley 31/1995'),
    ('LOC004', 'Atrapamientos', 'locativo', 'Atrapamiento por o entre máquinas o elementos móviles', 'RD 1215/1997'),
    ('LOC005', 'Volcamiento de vehículos', 'locativo', 'Caída o volcamiento de vehículos industriales', 'RD 1215/1997'),

    # Incendio y explosión
    ('INC001', 'Combustibles', 'incendio', 'Presencia de sustancias combustibles o inflamables', 'RD 2267/2004'),
    ('INC002', 'Fuentes de ignición', 'incendio', 'Presencia de fuentes de ignición en áreas con riesgo', 'RD 2267/2004'),
    ('INC003', 'Atmósferas explosivas (ATEX)', 'incendio', 'Presencia de atmósferas explosivas', 'RD 681/2003'),
    ('INC004', 'Oxígeno enriquecido', 'incendio', 'Riesgo por presencia de oxígeno en concentraciones superiores', 'RD 2267/2004'),

    # Otros
    ('OTR001', 'Derrames', 'otro', 'Riesgo por derrames de sustancias', 'Ley 31/1995'),
    ('OTR002', 'Inundaciones', 'otro', 'Riesgo por inundaciones o aguas acumuladas', 'Ley 31/1995'),
]


def crear_tipos_peligro(apps, schema_editor):
    TipoPeligro = apps.get_model('risk_assessment', 'TipoPeligro')

    for codigo, nombre, categoria, descripcion, ref_normativa in TIPOS_PELIGRO_INSST:
        TipoPeligro.objects.get_or_create(
            codigo=codigo,
            defaults={
                'nombre': nombre,
                'categoria': categoria,
                'descripcion': descripcion,
                'referencia_normativa': ref_normativa,
                'activo': True,
            }
        )


def eliminar_tipos_peligro(apps, schema_editor):
    TipoPeligro = apps.get_model('risk_assessment', 'TipoPeligro')
    codigos = [t[0] for t in TIPOS_PELIGRO_INSST]
    TipoPeligro.objects.filter(codigo__in=codigos).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('risk_assessment', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(crear_tipos_peligro, eliminar_tipos_peligro),
    ]
