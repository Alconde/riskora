from django.db import migrations


MEDIDAS = [
    # ── Mantenimiento de Instalaciones ──
    {
        'nombre': 'Revisión instalación eléctrica',
        'categoria': 'mantenimiento_instalaciones',
        'frecuencia_por_defecto': 'anual',
        'normativa': 'RD 614/2001, Reglamento Electrotécnico para Baja Tensión',
        'descripcion': 'Inspección y revisión periódica de la instalación eléctrica, cuadros, tomas de tierra y protecciones.',
    },
    {
        'nombre': 'Revisión instalación de gas',
        'categoria': 'mantenimiento_instalaciones',
        'frecuencia_por_defecto': 'anual',
        'normativa': 'RD 919/2006, Reglamento de Instalaciones Gasificadas',
        'descripcion': 'Revisión periódica de instalaciones de suministro y utilización de gases combustibles.',
    },
    {
        'nombre': 'Revisión ascensores y montacargas',
        'categoria': 'mantenimiento_instalaciones',
        'frecuencia_por_defecto': 'anual',
        'normativa': 'RD 995/2009, RD 2291/RIDAE',
        'descripcion': 'Inspección y mantenimiento de ascensores, montacargas y plataformas elevadoras.',
    },
    {
        'nombre': 'Revisión instalación de aire acondicionado y ventilación',
        'categoria': 'mantenimiento_instalaciones',
        'frecuencia_por_defecto': 'anual',
        'normativa': 'RD 1027/2007 (Reglamento de Instalaciones Térmicas)',
        'descripcion': 'Mantenimiento preventivo de equipos de climatización y sistemas de ventilación.',
    },
    {
        'nombre': 'Revisión calderas y recipientes a presión',
        'categoria': 'mantenimiento_instalaciones',
        'frecuencia_por_defecto': 'anual',
        'normativa': 'RD 2060/2008, RD 1036/2017',
        'descripcion': 'Inspección periódica de calderas, depósitos a presión y tuberías.',
    },
    {
        'nombre': 'Revisión sistemas de protección contra incendios (SPCI)',
        'categoria': 'mantenimiento_instalaciones',
        'frecuencia_por_defecto': 'semestral',
        'normativa': 'RD 513/2017, UNE 25690',
        'descripcion': 'Mantenimiento de extintores, bocas de incendio, rociadores y sistemas de detección.',
    },
    {
        'nombre': 'Revisión instalación de ventilación y extracción',
        'categoria': 'mantenimiento_instalaciones',
        'frecuencia_por_defecto': 'semestral',
        'normativa': 'RD 374/2001 (Asbestos), Ley 31/1995',
        'descripcion': 'Revisión de sistemas de ventilación general y captación en puntos de generación de contaminantes.',
    },
    {
        'nombre': 'Revisión fontanería y saneamiento',
        'categoria': 'mantenimiento_instalaciones',
        'frecuencia_por_defecto': 'anual',
        'normativa': 'R.D. de Suministro y Saneamiento',
        'descripcion': 'Inspección de redes de agua, desagües y sistemas de evacuación.',
    },

    # ── Mantenimiento de Equipos ──
    {
        'nombre': 'Revisión equipos de trabajo (herramientas, máquinas)',
        'categoria': 'mantenimiento_equipos',
        'frecuencia_por_defecto': 'trimestral',
        'normativa': 'RD 1215/1997, Art. 17-18 Ley 31/1995',
        'descripcion': 'Revisión periódica de herramientas manuales y máquinas para garantizar su buen estado.',
    },
    {
        'nombre': 'Revisión equipos de elevación y izaje',
        'categoria': 'mantenimiento_equipos',
        'frecuencia_por_defecto': 'semestral',
        'normativa': 'RD 809/2015, RD 1215/1997',
        'descripcion': 'Inspección de grúas, puentes grúa, eslingas, ganchos y aparejos de elevación.',
    },
    {
        'nombre': 'Revisión equipos de protección contra caídas',
        'categoria': 'mantenimiento_equipos',
        'frecuencia_por_defecto': 'semestral',
        'normativa': 'RD 1215/1997, UNE-EN 361/362/363',
        'descripcion': 'Revisión de arneses, líneas de vida, absorbentes de energía y anclajes.',
    },
    {
        'nombre': 'Revisión equipos de soldadura y corte',
        'categoria': 'mantenimiento_equipos',
        'frecuencia_por_defecto': 'trimestral',
        'normativa': 'RD 1215/1997, UNE-EN ISO 3834',
        'descripcion': 'Mantenimiento de equipos de soldadura, sopletes, reguladores y mangueras.',
    },
    {
        'nombre': 'Revisión herramienta manual',
        'categoria': 'mantenimiento_equipos',
        'frecuencia_por_defecto': 'trimestral',
        'normativa': 'RD 1215/1997, UNE-EN 576',
        'descripcion': 'Comprobación del estado de martillos, llaves, alicates, destornilladores y cuchillas.',
    },
    {
        'nombre': 'Revisión equipos de protección colectiva (EPC)',
        'categoria': 'mantenimiento_equipos',
        'frecuencia_por_defecto': 'semestral',
        'normativa': 'RD 1215/1997, Ley 31/1995 Art. 15',
        'descripcion': 'Inspección de barandillas, resguardos, dispositivos de enclavamiento y parada de emergencia.',
    },
    {
        'nombre': 'Calibración de instrumentos de medición',
        'categoria': 'mantenimiento_equipos',
        'frecuencia_por_defecto': 'anual',
        'normativa': 'UNE-EN ISO/IEC 17025',
        'descripcion': 'Calibración de detectores de gas, dosímetros, termómetros, manómetros y otros instrumentos.',
    },

    # ── Entrega y Control de EPIs ──
    {
        'nombre': 'Entrega periódica de EPIs',
        'categoria': 'entrega_epis',
        'frecuencia_por_defecto': 'anual',
        'normativa': 'RD 186/2008, Art. 15 Ley 31/1995',
        'descripcion': 'Entrega de equipos de protección individual según evaluación de riesgos: EPIs de cabeza, manos, pies, oídos, ojos, vías respiratorias.',
    },
    {
        'nombre': 'Revisión y sustitución de EPIs deteriorados',
        'categoria': 'entrega_epis',
        'frecuencia_por_defecto': 'trimestral',
        'normativa': 'RD 186/2008, UNE-EN normas aplicables',
        'descripcion': 'Comprobación del estado de los EPIs y sustitución de los deteriorados o caducados.',
    },
    {
        'nombre': 'Control de entrega y firma de EPIs',
        'categoria': 'entrega_epis',
        'frecuencia_por_defecto': 'continua',
        'normativa': 'RD 186/2008',
        'descripcion': 'Registro de entrega de EPIs con firma del trabajador y conservación de la documentación.',
    },

    # ── Inspecciones ──
    {
        'nombre': 'Inspección periódica de seguridad',
        'categoria': 'inspecciones',
        'frecuencia_por_defecto': 'trimestral',
        'normativa': 'Art. 16 Ley 31/1995, RD 39/1997 Art. 17-20',
        'descripcion': 'Ronda de inspección visual para detectar deficiencias, comportamientos inseguros y condiciones peligrosas.',
    },
    {
        'nombre': 'Auditoría interna de PRL',
        'categoria': 'inspecciones',
        'frecuencia_por_defecto': 'anual',
        'normativa': 'ISO 45001, RD 39/1997',
        'descripcion': 'Evaluación sistemática del sistema de gestión de prevención de riesgos laborales.',
    },
    {
        'nombre': 'Inspección de puestos de trabajo',
        'categoria': 'inspecciones',
        'frecuencia_por_defecto': 'semestral',
        'normativa': 'Art. 16 Ley 31/1995, RD 39/1997',
        'descripcion': 'Evaluación específica de las condiciones de cada puesto de trabajo: ergonomía, iluminación, ruido, etc.',
    },
    {
        'nombre': 'Inspección de vías de circulación y zonas de riesgo',
        'categoria': 'inspecciones',
        'frecuencia_por_defecto': 'trimestral',
        'normativa': 'RD 1215/1997, RD 1032/2007',
        'descripcion': 'Revisión de pasillos, escaleras, plataformas, zonas peatonales y de riesgo.',
    },
    {
        'nombre': 'Control ambiental (ruido, iluminación, temperatura)',
        'categoria': 'inspecciones',
        'frecuencia_por_defecto': 'semestral',
        'normativa': 'RD 1027/2007, RD 486/1997, RD 286/2006',
        'descripcion': 'Medición de niveles de ruido, niveles de iluminación, condiciones térmicas y calidad del aire.',
    },

    # ── Formación y Capacitación ──
    {
        'nombre': 'Formación preventiva a trabajadores',
        'categoria': 'formacion',
        'frecuencia_por_defecto': 'anual',
        'normativa': 'Art. 19 Ley 31/1995, RD 39/1997 Art. 28',
        'descripcion': 'Formación en riesgos generales y específicos del puesto, medidas de prevención y protección.',
    },
    {
        'nombre': 'Formación específica por puesto de trabajo',
        'categoria': 'formacion',
        'frecuencia_por_defecto': 'anual',
        'normativa': 'Art. 19 Ley 31/1995',
        'descripcion': 'Capacitación en riesgos específicos del puesto: maquinaria peligrosa, sustancias químicas, etc.',
    },
    {
        'nombre': 'Simulacros de emergencia y evacuación',
        'categoria': 'formacion',
        'frecuencia_por_defecto': 'anual',
        'normativa': 'RD 393/2007, Art. 20 Ley 31/1995',
        'descripcion': 'Ejercicios prácticos de evacuación, actuación ante incendios y primeros auxilios.',
    },
    {
        'nombre': 'Formación en uso de EPIs',
        'categoria': 'formacion',
        'frecuencia_por_defecto': 'anual',
        'normativa': 'RD 186/2008, Art. 19 Ley 31/1995',
        'descripcion': 'Capacitación en el correcto uso, mantenimiento y limitaciones de los EPIs asignados.',
    },
    {
        'nombre': 'Formación en primeros auxilios',
        'categoria': 'formacion',
        'frecuencia_por_defecto': 'anual',
        'normativa': 'Art. 19 Ley 31/1995',
        'descripcion': 'Formación práctica en RCP, traumatismos, hemorragias y actuación ante emergencias.',
    },

    # ── Vigilancia de la Salud ──
    {
        'nombre': 'Reconocimiento médico periódico',
        'categoria': 'vigilancia_salud',
        'frecuencia_por_defecto': 'anual',
        'normativa': 'Art. 22 Ley 31/1995, RD 39/1997 Art. 37',
        'descripcion': 'Examen médico según protocolo de vigilancia de la salud: audiometría, espirometría, etc.',
    },
    {
        'nombre': 'Seguimiento de trabajadores sensibilizados',
        'categoria': 'vigilancia_salud',
        'frecuencia_por_defecto': 'semestral',
        'normativa': 'Art. 22 Ley 31/1995',
        'descripcion': 'Vigilancia especial de trabajadores con patologías previas o factores de riesgo.',
    },
    {
        'nombre': 'Vigilancia ambiental (exposiciones químicas, biológicas)',
        'categoria': 'vigilancia_salud',
        'frecuencia_por_defecto': 'semestral',
        'normativa': 'RD 374/2001, RD 664/1997',
        'descripcion': 'Medición de agentes químicos y biológicos y comparación con valores límite.',
    },

    # ── Limpieza y Higiene ──
    {
        'nombre': 'Limpieza y desinfección periódica de zonas de trabajo',
        'categoria': 'limpieza_higiene',
        'frecuencia_por_defecto': 'semanal',
        'normativa': 'Ley 31/1995 Art. 15, RD 39/1997',
        'descripcion': 'Limpieza programada de puestos de trabajo, suelos, superficies y zonas comunes.',
    },
    {
        'nombre': 'Limpieza de sistemas de ventilación y extracción',
        'categoria': 'limpieza_higiene',
        'frecuencia_por_defecto': 'semestral',
        'normativa': 'RD 374/2001, Ley 31/1995',
        'descripcion': 'Limpieza de conductos, filtros y rejillas de ventilación y extracción.',
    },
    {
        'nombre': 'Control de plagas y desinfección',
        'categoria': 'limpieza_higiene',
        'frecuencia_por_defecto': 'trimestral',
        'normativa': 'Real Decreto sanitario',
        'descripcion': 'Tratamiento periódico contra plagas (roedores, insectos) y desinfección de instalaciones.',
    },

    # ── Emergencias ──
    {
        'nombre': 'Revisión y actualización del Plan de Emergencia',
        'categoria': 'emergencias',
        'frecuencia_por_defecto': 'anual',
        'normativa': 'RD 393/2007, Art. 20 Ley 31/1995',
        'descripcion': 'Revisión del plan de emergencia, actualización de contactos, rutas y recursos.',
    },
    {
        'nombre': 'Revisión de equipos de socorro y primeros auxilios',
        'categoria': 'emergencias',
        'frecuencia_por_defecto': 'trimestral',
        'normativa': 'RD 393/2007, Normativa UNE',
        'descripcion': 'Comprobación de botiquines, mantas ignífugas, DEA, material de rescate.',
    },
    {
        'nombre': 'Mantenimiento de salidas de emergencia',
        'categoria': 'emergencias',
        'frecuencia_por_defecto': 'trimestral',
        'normativa': 'RD 393/2007, DB-SI (Código Técnico)',
        'descripcion': 'Verificación de que las salidas de emergencia están libres, señalizadas e iluminadas.',
    },

    # ── Señalización y Documentación ──
    {
        'nombre': 'Revisión de señalización de seguridad',
        'categoria': 'senalizacion_documentacion',
        'frecuencia_por_defecto': 'semestral',
        'normativa': 'ISO 7010, RD 485/1997',
        'descripcion': 'Comprobación del estado de señales de prohibición, advertencia, obligación y emergencia.',
    },
    {
        'nombre': 'Actualización de documentación preventiva',
        'categoria': 'senalizacion_documentacion',
        'frecuencia_por_defecto': 'anual',
        'normativa': 'Art. 16-23 Ley 31/1995, RD 39/1997',
        'descripcion': 'Revisión y actualización de: evaluación de riesgos, plan de prevención, protocolos, instrucciones.',
    },
    {
        'nombre': 'Actualización de fichas de seguridad (FDS)',
        'categoria': 'senalizacion_documentacion',
        'frecuencia_por_defecto': 'anual',
        'normativa': 'REACH (CE 1907/2006), CLP (EC 1272/2008)',
        'descripcion': 'Verificación de que las Fichas de Datos de Seguridad están actualizadas y accesibles.',
    },
]


def forwards(apps, schema_editor):
    MedidaPreventivaCatalogo = apps.get_model('preventive_planning', 'MedidaPreventivaCatalogo')
    for m in MEDIDAS:
        MedidaPreventivaCatalogo.objects.get_or_create(
            nombre=m['nombre'],
            defaults={
                'categoria': m['categoria'],
                'frecuencia_por_defecto': m['frecuencia_por_defecto'],
                'normativa': m['normativa'],
                'descripcion': m['descripcion'],
                'company_id': None,
            },
        )


def backwards(apps, schema_editor):
    MedidaPreventivaCatalogo = apps.get_model('preventive_planning', 'MedidaPreventivaCatalogo')
    MedidaPreventivaCatalogo.objects.filter(company_id__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('preventive_planning', '0002_add_medida_preventiva_catalogo'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
