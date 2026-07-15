import random
import sys
from datetime import date, timedelta
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.companies.models import Company, CompanyMembership

if sys.platform == 'win32' and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

User = get_user_model()


def _ph(content):
    f = ContentFile(content.encode('utf-8'), name='placeholder.txt')
    return f


class Command(BaseCommand):
    help = (
        'Carga datos ficticios completos: 4 empresas (A y B bien documentadas, '
        'C y D con deficiencias). Cubre todos los módulos de la aplicación.'
    )

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('Cargando datos ficticios de prueba...\n'))

        # ══════════════════════════════════════════════════════════════════
        #  REFERENCIAS GLOBALES
        # ══════════════════════════════════════════════════════════════════
        self._cargar_niveles_riesgo()
        self._cargar_marcos_legales()

        # ══════════════════════════════════════════════════════════════════
        #  USUARIOS
        # ══════════════════════════════════════════════════════════════════
        usuarios = self._crear_usuarios()

        # ══════════════════════════════════════════════════════════════════
        #  EMPRESA A — INDUSTRIAS ALONSO (Bien documentada)
        # ══════════════════════════════════════════════════════════════════
        emp_a = self._crear_empresa_a(usuarios)

        # ══════════════════════════════════════════════════════════════════
        #  EMPRESA B — GRUPO NORTE LOGÍSTICA (Bien documentada)
        # ══════════════════════════════════════════════════════════════════
        emp_b = self._crear_empresa_b(usuarios)

        # ══════════════════════════════════════════════════════════════════
        #  EMPRESA C — CONSTRUCCIONES RÁPIDA SUR (Mal documentada ~40%)
        # ══════════════════════════════════════════════════════════════════
        emp_c = self._crear_empresa_c(usuarios)

        # ══════════════════════════════════════════════════════════════════
        #  EMPRESA D — TALLERES MECÁNICOS EL MOTOR (Desastre ~10%)
        # ══════════════════════════════════════════════════════════════════
        emp_d = self._crear_empresa_d(usuarios)

        # ══════════════════════════════════════════════════════════════════
        #  RESUMEN FINAL
        # ══════════════════════════════════════════════════════════════════
        self._resumen(usuarios)

    # ══════════════════════════════════════════════════════════════════════
    #  NIVELES DE RIESGO (Tabla de referencia INSST)
    # ══════════════════════════════════════════════════════════════════════
    def _cargar_niveles_riesgo(self):
        from apps.risk_assessment.models import NivelRiesgoReferencia
        niveles = [
            (1, 1, 1, 'muy_bajo', 'Muy bajo', '#22c55e', '#f0fdf4', '#166534',
             'Riesgo despreciable, sin necesidad de medida adicional'),
            (2, 1, 2, 'bajo', 'Bajo', '#84cc16', '#f7fee7', '#3f6212',
             'Riesgo bajo, medidas preventivas habituales'),
            (3, 1, 3, 'medio', 'Medio', '#eab308', '#fefce8', '#854d0e',
             'Riesgo medio, se requieren medidas preventivas específicas'),
            (4, 2, 2, 'medio', 'Medio', '#eab308', '#fefce8', '#854d0e',
             'Riesgo medio, se requieren medidas preventivas específicas'),
            (5, 2, 3, 'alto', 'Alto', '#f97316', '#fff7ed', '#9a3412',
             'Riesgo alto, necesidad de medidas de protección colectiva y/o EPIs'),
            (6, 3, 2, 'alto', 'Alto', '#f97316', '#fff7ed', '#9a3412',
             'Riesgo alto, necesidad de medidas de protección colectiva y/o EPIs'),
            (7, 3, 3, 'muy_alto', 'Muy alto', '#ef4444', '#fef2f2', '#991b1b',
             'Riesgo muy alto, paralización del trabajo hasta reducir el riesgo'),
            (8, 2, 1, 'bajo', 'Bajo', '#84cc16', '#f7fee7', '#3f6212',
             'Riesgo bajo, medidas preventivas habituales'),
            (9, 3, 1, 'medio', 'Medio', '#eab308', '#fefce8', '#854d0e',
             'Riesgo medio, se requieren medidas preventivas específicas'),
        ]
        for grado, prob, sev, nivel, etiqueta, color, fondo, texto, desc in niveles:
            NivelRiesgoReferencia.objects.get_or_create(
                grado=grado,
                defaults={
                    'probabilidad': prob, 'severidad': sev, 'nivel': nivel,
                    'etiqueta': etiqueta, 'color': color, 'color_fondo': fondo,
                    'color_texto': texto, 'descripcion': desc,
                }
            )
        self.stdout.write(self.style.SUCCESS('  Niveles de riesgo INSST: 9 referencias creadas'))

    # ══════════════════════════════════════════════════════════════════════
    #  MARCO LEGAL (Normativa y Requisitos)
    # ══════════════════════════════════════════════════════════════════════
    def _cargar_marcos_legales(self):
        from apps.legal_requirements.models import NormativaLegal, RequisitoLegal

        normativas_data = [
            ('Ley 31/1995 de Prevención de Riesgos Laborales', 'ley', '31/1995', 'estatal',
             date(1995, 11, 8), 'Ley marco de prevención de riesgos laborales en España'),
            ('Real Decreto 39/1997 Reglamento de Servicios de Prevención', 'real_decreto', '39/1997', 'estatal',
             date(1997, 1, 14), 'Regula los servicios de prevención y actividades preventivas'),
            ('Real Decreto 486/1997 Lugares de trabajo', 'real_decreto', '486/1997', 'estatal',
             date(1997, 5, 14), 'Requisitos mínimos de seguridad en lugares de trabajo'),
            ('Real Decreto 1215/1997 Uso de EPIs', 'real_decreto', '1215/1997', 'estatal',
             date(1997, 10, 17), 'Normas de utilización de equipos de protección individual'),
            ('Real Decreto 842/2002 Instalaciones eléctricas', 'real_decreto', '842/2002', 'estatal',
             date(2002, 7, 26), 'Requisitos de seguridad en instalaciones eléctricas'),
            ('Ley 17/2005 Conciliación de la vida familiar y laboral', 'ley', '17/2005', 'estatal',
             date(2005, 7, 12), 'Flexibilización de la jornada laboral'),
            ('Real Decreto 664/1997 Agentes biológicos', 'real_decreto', '664/1997', 'estatal',
             date(1997, 5, 12), 'Protección de los trabajadores contra riesgos biológicos'),
            ('Real Decreto 1627/1997 Coordinación de actividades', 'real_decreto', '1627/1997', 'estatal',
             date(1997, 11, 14), 'Medidas de coordinación de empresas en actividades concurrentes'),
        ]

        normativas = []
        for nombre, tipo, numero, ambito, fecha, resumen in normativas_data:
            n, _ = NormativaLegal.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'tipo': tipo, 'numero': numero, 'ambito': ambito,
                    'fecha_publicacion': fecha, 'fecha_vigencia': fecha,
                    'resumen': resumen, 'activa': True,
                }
            )
            normativas.append(n)

        requisitos_data = [
            (normativas[0], 'Plan de prevención obligatorio', 'Elaborar y mantener actualizado el plan de prevención', 'prevencion', 'Art. 16'),
            (normativas[0], 'Evaluación de riesgos periódica', 'Realizar evaluación de riesgos y actualizar periódicamente', 'prevencion', 'Art. 16'),
            (normativas[0], 'Formación de trabajadores', 'Formar a los trabajadores en materia preventiva', 'formacion', 'Art. 18'),
            (normativas[0], 'Vigilancia de la salud', 'Vigilancia periódica de la salud de los trabajadores', 'vigilancia', 'Art. 22'),
            (normativas[0], 'Información a trabajadores', 'Informar a los trabajadores sobre riesgos y medidas de prevención', 'prevencion', 'Art. 18'),
            (normativas[1], 'Servicio de prevención propio', 'Constitución de servicio de prevención propio si >500 trabajadores', 'prevencion', 'Art. 15'),
            (normativas[1], 'Coordinación de actividades preventivas', 'Designar coordinador de actividades preventivas', 'prevencion', 'Art. 15'),
            (normativas[2], 'Condiciones de los lugares de trabajo', 'Requisitos mínimos de seguridad y salud en los lugares de trabajo', 'instalaciones', 'Art. 4'),
            (normativas[2], 'Señalización de seguridad', 'Señalización de zonas de peligro y rutas de evacuación', 'instalaciones', 'Art. 8'),
            (normativas[3], 'Entrega y mantenimiento de EPIs', 'Proporcionar EPIs homologados y en buen estado', 'epis', 'Art. 4'),
            (normativas[3], 'Formación en uso de EPIs', 'Formar en el uso correcto de los EPIs', 'epis', 'Art. 5'),
            (normativas[4], 'Revisiones periódicas de instalaciones', 'Revisiones eléctricas según periodically', 'instalaciones', 'Art. 6'),
            (normativas[5], 'Adaptación del tiempo de trabajo', 'Medidas de conciliación de vida laboral y familiar', 'otros', 'Art. 34'),
            (normativas[6], 'Protección frente a agentes biológicos', 'Medidas de protección y vigilancia sanitaria', 'epis', 'Art. 5'),
            (normativas[7], 'Plan de emergencia y evacuación', 'Establecer plan de emergencia y realizar simulacros', 'emergencias', 'Art. 5'),
        ]

        requisitos = []
        for norm, titulo, desc, cat, art in requisitos_data:
            r, _ = RequisitoLegal.objects.get_or_create(
                normativa=norm, titulo=titulo,
                defaults={
                    'descripcion': desc, 'categoria': cat, 'articulo': art,
                }
            )
            requisitos.append(r)

        self._requisitos_legales = requisitos
        self.stdout.write(self.style.SUCCESS(
            f'  Marco legal: {len(normativas)} normativas, {len(requisitos)} requisitos'
        ))

    # ══════════════════════════════════════════════════════════════════════
    #  USUARIOS
    # ══════════════════════════════════════════════════════════════════════
    def _crear_usuarios(self):
        usuarios = {}

        data = [
            ('admin_test', 'admin@riskora-test.com', 'Admin', 'Sistema', True, True, 'admin'),
            ('ana_alonso', 'ana@alonso-test.com', 'Ana', 'Alonso Martínez', False, False, 'admin'),
            ('pedro_tecnico', 'pedro@alonso-test.com', 'Pedro', 'Gómez Serrano', False, False, 'technician'),
            ('laura_norte', 'laura@norte-test.com', 'Laura', 'Bilbao Fernández', False, False, 'admin'),
            ('carlos_tecnico', 'carlos@norte-test.com', 'Carlos', 'Ruiz Martín', False, False, 'technician'),
            ('jorge_rapida', 'jorge@rapida-test.com', 'Jorge', 'Navas Ríos', False, False, 'admin'),
            ('maria_motor', 'maria@motor-test.com', 'María', 'Cano Herrera', False, False, 'admin'),
        ]

        for uname, email, fn, ln, staff, superu, role in data:
            user, created = User.objects.get_or_create(
                username=uname,
                defaults={
                    'email': email, 'first_name': fn, 'last_name': ln,
                    'is_staff': staff, 'is_superuser': superu,
                    'role': role, 'is_verified': True,
                },
            )
            user.set_password('test1234')
            user.save()
            usuarios[uname] = user

        self.stdout.write(self.style.SUCCESS(
            '  Usuarios creados: ' + ', '.join(f'{u} / test1234' for u in usuarios)
        ))
        return usuarios

    # ══════════════════════════════════════════════════════════════════════
    #  HELPER: Crear empresa base
    # ══════════════════════════════════════════════════════════════════════
    def _empresa(self, tax_id, legal_name, trade_name, **kw):
        defaults = {
            'legal_name': legal_name, 'trade_name': trade_name,
            'email': kw.get('email', ''), 'phone': kw.get('phone', ''),
            'address': kw.get('address', ''), 'postal_code': kw.get('postal_code', ''),
            'city': kw.get('city', ''), 'province': kw.get('province', ''),
            'autonomous_community': kw.get('ac', ''),
            'activity': kw.get('activity', ''), 'cnae': kw.get('cnae', ''),
            'workforce_size': kw.get('workforce', 0), 'status': 'active',
        }
        emp, _ = Company.objects.get_or_create(tax_id=tax_id, defaults=defaults)
        return emp

    def _membresia(self, user, empresa, role='company_admin', default=False):
        CompanyMembership.objects.get_or_create(
            user=user, company=empresa,
            defaults={'role': role, 'is_active': True, 'is_default': default},
        )

    def _centro(self, empresa, **kw):
        from apps.workcenters.models import WorkCenter
        c, _ = WorkCenter.objects.get_or_create(
            company=empresa, name=kw['name'],
            defaults={
                'code': kw.get('code', ''), 'address': kw.get('address', ''),
                'postal_code': kw.get('postal_code', ''), 'city': kw.get('city', ''),
                'province': kw.get('province', ''), 'activity': kw.get('activity', ''),
                'worker_count': kw.get('workers', 0), 'risk_level': kw.get('risk', 'medium'),
            }
        )
        return c

    def _puesto(self, empresa, nombre, dept='General'):
        from apps.workers.models import JobPosition
        p, _ = JobPosition.objects.get_or_create(
            company=empresa, name=nombre,
            defaults={'department': dept, 'status': 'active'}
        )
        return p

    def _trabajador(self, empresa, fn, ln, nif, centro, puesto):
        from apps.workers.models import Worker
        w, _ = Worker.objects.get_or_create(
            company=empresa, national_id=nif,
            defaults={
                'first_name': fn, 'last_name': ln,
                'work_center': centro, 'job_position': puesto,
                'employment_status': 'active',
                'hire_date': date(2020, 1, 15) + timedelta(days=random.randint(0, 1200)),
            }
        )
        return w

    def _doc_cat(self, name, slug, mandatory=True):
        from apps.documents.models import DocumentCategory
        cat, _ = DocumentCategory.objects.get_or_create(
            name=name, defaults={
                'slug': slug, 'scope': 'company',
                'is_mandatory': mandatory, 'is_active': True,
            }
        )
        return cat

    def _documento(self, empresa, categoria, titulo, user, status='valid', **kw):
        from apps.documents.models import Document
        doc, created = Document.objects.get_or_create(
            company=empresa, title=titulo,
            defaults={
                'category': categoria, 'description': kw.get('desc', titulo),
                'file': _ph(f'Documento de prueba: {titulo}'),
                'version': kw.get('version', '1.0'),
                'code': kw.get('code', ''),
                'issue_date': kw.get('issue', date.today() - timedelta(days=90)),
                'expiry_date': kw.get('expiry', date.today() + timedelta(days=275)),
                'status': status, 'uploaded_by': user,
            }
        )
        return doc

    # ══════════════════════════════════════════════════════════════════════
    #  EMPRESA A — INDUSTRIAS ALONSO Y MARTÍNEZ S.L. (COMPLETA)
    # ══════════════════════════════════════════════════════════════════════
    def _crear_empresa_a(self, u):
        self.stdout.write(self.style.MIGRATE_HEADING(
            '\n-- EMPRESA A: Industrias Alonso y Martinez S.L. (COMPLETA) --'
        ))
        emp = self._empresa(
            'B87654321', 'Industrias Alonso y Martínez S.L.', 'Alonso Industria',
            email='info@alonso-test.com', phone='913456789',
            address='Calle de la Industria, 42', postal_code='28010',
            city='Madrid', province='Madrid', ac='Comunidad de Madrid',
            activity='Fabricación de componentes metálicos', cnae='2511', workforce=85,
        )
        admin, tech = u['ana_alonso'], u['pedro_tecnico']
        self._membresia(admin, emp, 'company_admin', True)
        self._membresia(tech, emp, 'technician')
        self._membresia(u['admin_test'], emp, 'company_admin', False)

        # ── Centros de trabajo ──
        c1 = self._centro(emp, name='Fábrica Principal', code='FP-001',
                          address='C/ Industria 42', postal_code='28010', city='Madrid',
                          province='Madrid', activity='Fabricación', workers=55, risk='high')
        c2 = self._centro(emp, name='Oficinas Centrales', code='OC-001',
                          address='C/ Industria 40', postal_code='28010', city='Madrid',
                          province='Madrid', activity='Administración', workers=20, risk='low')
        c3 = self._centro(emp, name='Almacén Sur', code='AS-001',
                          address='Polígono Sur 15', postal_code='28020', city='Madrid',
                          province='Madrid', activity='Almacenaje', workers=10, risk='medium')

        # ── Puestos de trabajo ──
        p0 = self._puesto(emp, 'Responsable de Producción', 'Producción')
        p1 = self._puesto(emp, 'Operario de Máquina CNC', 'Producción')
        p2 = self._puesto(emp, 'Soldador', 'Producción')
        p3 = self._puesto(emp, 'Montador Industrial', 'Producción')
        p4 = self._puesto(emp, 'Técnico de Mantenimiento', 'Mantenimiento')
        p5 = self._puesto(emp, 'Encargado de Almacén', 'Almacén')
        p6 = self._puesto(emp, 'Operario de Almacén', 'Almacén')
        p7 = self._puesto(emp, 'Administrativo', 'Administración')
        p8 = self._puesto(emp, 'Técnico de PRL', 'Prevención')
        p9 = self._puesto(emp, 'Director de Planta', 'Dirección')

        # ── Trabajadores ──
        t = []
        tdata = [
            ('Ana', 'Martínez Ruiz', '28123456A', c1, p0),
            ('Pedro', 'Sánchez López', '28234567B', c1, p1),
            ('Lucía', 'Fernández García', '28345678C', c1, p2),
            ('Miguel', 'Rodríguez Pérez', '28456789D', c1, p3),
            ('Carmen', 'Díaz Moreno', '28567890E', c1, p4),
            ('Juan', 'Torres Navarro', '28678901F', c2, p7),
            ('Laura', 'Jiménez Vidal', '28789012G', c3, p5),
            ('Francisco', 'López Castillo', '28890123H', c3, p6),
            ('Isabel', 'Hernández Romero', '28901234I', c2, p8),
            ('Roberto', 'Moreno Salas', '28012345J', c1, p9),
        ]
        for fn, ln, nif, centro, puesto in tdata:
            t.append(self._trabajador(emp, fn, ln, nif, centro, puesto))
        self.stdout.write(f'  Centros: 3 | Puestos: 10 | Trabajadores: {len(t)}')

        # ── Plan de Prevención ──
        from apps.prevention_plan.models import PlanPrevention
        PlanPrevention.objects.get_or_create(
            company=emp,
            defaults={
                'politica_firmada': True,
                'delegado_prl': 'si', 'delegado_fecha_designacion': date(2024, 1, 15),
                'delegado_formacion': True,
                'doc_designacion_delegado': _ph('Designación delegado PRL'),
                'doc_formacion_delegado': _ph('Formación delegado PRL'),
                'recurso_preventivo': 'si',
                'recurso_actividades': 'Todas las actividades preventivas',
                'recurso_fecha_designacion': date(2024, 1, 15),
                'recurso_formacion': True,
                'doc_designacion_recurso': _ph('Designación recurso preventivo'),
                'doc_formacion_recurso': _ph('Formación recurso preventivo'),
                'organigrama_texto': 'Director → Técnico PRL → Delegados de sección',
                'funciones_responsabilidades': 'Funciones según art. 15 LPRL',
                'utiliza_ett': False, 'tiene_teletrabajo': False,
            },
        )
        self.stdout.write('  Plan de Prevención: completo')

        # ── Evaluación de Riesgos ──
        from apps.risk_assessment.models import TipoPeligro, EvaluacionRiesgos, ItemEvaluacionRiesgos
        peligros = []
        for cod, nombre, cat in [
            ('MEC-001', 'Riesgo mecánico', 'mecanico'),
            ('QUI-001', 'Riesgo químico', 'quimico'),
            ('ELE-001', 'Riesgo eléctrico', 'electrico'),
            ('ERG-001', 'Riesgo ergonómico', 'ergonomico'),
            ('PSI-001', 'Riesgo psicosocial', 'psicosocial'),
            ('FIS-001', 'Riesgo físico (ruido)', 'fisico'),
            ('LOC-001', 'Riesgo locativo (caídas)', 'locativo'),
            ('INC-001', 'Riesgo de incendio', 'incendio'),
        ]:
            p, _ = TipoPeligro.objects.get_or_create(
                codigo=cod, defaults={'nombre': nombre, 'categoria': cat, 'descripcion': nombre}
            )
            peligros.append(p)

        ev, _ = EvaluacionRiesgos.objects.get_or_create(
            empresa=emp, centro_trabajo=c1,
            titulo='Evaluación de Riesgos Fábrica Principal 2024',
            defaults={
                'fecha_evaluacion': date(2024, 3, 15), 'fecha_proxima_revision': date(2025, 3, 15),
                'metodologia': 'propio', 'revisado_por': admin, 'aprobado_por': admin,
                'fecha_aprobacion': date(2024, 3, 20), 'estado': 'aprobada', 'version': '2.0',
            }
        )
        ev2, _ = EvaluacionRiesgos.objects.get_or_create(
            empresa=emp, centro_trabajo=c2,
            titulo='Evaluación de Riesgos Oficinas 2024',
            defaults={
                'fecha_evaluacion': date(2024, 5, 10), 'fecha_proxima_revision': date(2025, 5, 10),
                'metodologia': 'propio', 'revisado_por': admin, 'aprobado_por': admin,
                'fecha_aprobacion': date(2024, 5, 15), 'estado': 'aprobada', 'version': '1.0',
            }
        )

        items_eval = [
            (ev, p1, peligros[0], 'Operación CNC', 2, 2, 'Mallas protectoras, EPIs', 'implementada'),
            (ev, p2, peligros[0], 'Soldadura', 3, 3, 'EPP completo, ventilación', 'implementada'),
            (ev, p3, peligros[6], 'Montaje en altura', 2, 3, 'Arnés, andamios', 'implementada'),
            (ev, p0, peligros[4], 'Supervisión', 1, 1, 'Jornada controlada', 'implementada'),
            (ev, p5, peligros[5], 'Zona de carga', 2, 2, 'Protección auditiva', 'implementada'),
            (ev2, p7, peligros[3], 'Oficina', 1, 1, 'Pantalla antirreflejo, descansos', 'implementada'),
        ]
        for evaluacion, puesto, peligro, factor, prob, sever, medidas, estado in items_eval:
            ItemEvaluacionRiesgos.objects.get_or_create(
                evaluacion=evaluacion, puesto_trabajo=puesto, tipo_peligro=peligro,
                defaults={
                    'tipo_riesgo': 'no_evitable', 'factor_riesgo_condicion': factor,
                    'medidas_existentes': medidas, 'probabilidad': prob, 'severidad': sever,
                    'medidas_propuestas': f'Mejora de {medidas.lower()}',
                    'estado_implementacion': estado,
                }
            )
        self.stdout.write('  Evaluación de Riesgos: 2 evaluaciones con 6 items')

        # ── Formación ──
        from apps.training.models import TrainingCategory, TrainingCourse, TrainingRecord
        cat_b, _ = TrainingCategory.objects.get_or_create(
            name='Formación Básica', defaults={'code': 'FB', 'description': 'Formación general PRL'}
        )
        cat_e, _ = TrainingCategory.objects.get_or_create(
            name='Formación Específica', defaults={'code': 'FE', 'description': 'Formación por puesto'}
        )
        cat_em, _ = TrainingCategory.objects.get_or_create(
            name='Emergencias', defaults={'code': 'EM', 'description': 'Formación en emergencias'}
        )
        cursos = []
        for cat, nombre, horas, oblig, renov, code in [
            (cat_b, 'Prevención de Riesgos Laborales Básica', 6, True, False, 'FB-001'),
            (cat_e, 'Trabajo en Altura', 8, True, True, 'FE-001'),
            (cat_e, 'Manipulador de Productos Químicos', 4, True, True, 'FE-002'),
            (cat_em, 'Primeros Auxilios', 16, True, True, 'EM-001'),
            (cat_em, 'Evacuación y Simulacros', 4, True, False, 'EM-002'),
            (cat_e, 'Operación de Carretillas Elevadoras', 8, True, True, 'FE-003'),
        ]:
            c, _ = TrainingCourse.objects.get_or_create(
                company=emp, name=nombre,
                defaults={
                    'category': cat, 'duration_hours': horas, 'is_mandatory': oblig,
                    'requires_renewal': renov, 'modality': 'presential',
                    'validity_value': 12 if renov else None,
                    'validity_unit': 'months' if renov else '', 'status': 'active',
                    'code': code,
                }
            )
            cursos.append(c)

        reg_count = 0
        for trab in t[:8]:
            for curso in random.sample(cursos, min(4, len(cursos))):
                if random.random() > 0.15:
                    TrainingRecord.objects.get_or_create(
                        company=emp, worker=trab, course=curso,
                        completed_date=date(2024, random.randint(1, 12), random.randint(1, 28)),
                        defaults={
                            'status': 'completed', 'planned_date': date(2024, 1, 1),
                            'trainer_name': 'Formador externo', 'training_entity': 'Instituto de Seguridad',
                            'created_by': admin,
                        }
                    )
                    reg_count += 1
        self.stdout.write(f'  Formación: {len(cursos)} categorías/cursos, {reg_count} registros')

        # ── Documentos ──
        cats_doc = {}
        for nombre, slug, oblig in [
            ('Plan de Prevención', 'plan-prevencion', True),
            ('Evaluación de Riesgos', 'evaluacion-riesgos', True),
            ('Protocolo de Emergencia', 'emergencias', True),
            ('Procedimiento de Trabajo Seguro', 'procedimientos', True),
            ('Política de Formación', 'formacion', False),
            ('Registro de EPIs', 'epis', True),
        ]:
            cats_doc[slug] = self._doc_cat(nombre, slug, oblig)

        docs_creados = 0
        docs_info = [
            ('plan-prevencion', 'Plan de Prevención 2024', 'PP-2024-001', 'Plan actualizado completo'),
            ('evaluacion-riesgos', 'Evaluación Riesgos Fábrica', 'ER-2024-001', 'Evaluación con matriz de riesgos'),
            ('evaluacion-riesgos', 'Evaluación Riesgos Oficinas', 'ER-2024-002', 'Evaluación entorno administrativo'),
            ('emergencias', 'Protocolo de Emergencia General', 'EM-2024-001', 'Protocolo de actuación ante emergencias'),
            ('emergencias', 'Plan de Evacuación', 'EM-2024-002', 'Planos y rutas de evacuación'),
            ('procedimientos', 'PTO Soldadura', 'PT-001', 'Procedimiento de trabajo seguro para soldadura'),
            ('procedimientos', 'PTO Trabajo en Altura', 'PT-002', 'Procedimiento de trabajo en altura'),
            ('procedimientos', 'PTO Manipulación Químicos', 'PT-003', 'Procedimiento para sustancias químicas'),
            ('formacion', 'Programa Formación Anual', 'PF-2024-001', 'Programa de formación del año'),
            ('epis', 'Inventario EPIs Actualizado', 'EP-2024-001', 'Relación de EPIs asignados'),
            ('epis', 'Registro Entregas EPIs', 'EP-2024-002', 'Control de entregas de EPIs'),
        ]
        for slug, titulo, code, desc in docs_info:
            self._documento(emp, cats_doc[slug], titulo, admin, code=code, desc=desc)
            docs_creados += 1
        self.stdout.write(f'  Documentos: {docs_creados} documentos en {len(cats_doc)} categorías')

        # ── Inspecciones ──
        from apps.inspections.models import PlantillaInspeccion, PlantillaInspeccionItem, Inspeccion, ItemInspeccion
        plantilla, _ = PlantillaInspeccion.objects.get_or_create(
            empresa=emp, nombre='Inspección de Seguridad General',
            defaults={'categoria': 'seguridad', 'descripcion': 'Inspección periódica de seguridad en fábrica'}
        )
        items_plantilla = [
            'Estado de pasillos y salidas de emergencia', 'Señalización de seguridad visible',
            'Estado de EPIs en uso', 'Extintores revisados y accesibles',
            'Estado de maquinaria y protecciones', 'Almacenamiento correcto de productos químicos',
            'Instalaciones eléctricas en buen estado',
        ]
        for i, desc in enumerate(items_plantilla, 1):
            PlantillaInspeccionItem.objects.get_or_create(
                plantilla=plantilla, orden=i, defaults={'descripcion': desc}
            )

        insp, _ = Inspeccion.objects.get_or_create(
            empresa=emp, centro_trabajo=c1, fecha_inspeccion=date(2024, 11, 15),
            defaults={
                'plantilla': plantilla, 'inspector': admin, 'estado': 'completada',
                'resultado_general': 'conforme', 'observaciones': 'Todas las áreas en buen estado',
                'nc_generadas': False, 'creado_por': admin,
            }
        )
        for i, desc in enumerate(items_plantilla, 1):
            ItemInspeccion.objects.get_or_create(
                inspeccion=insp, orden=i, defaults={
                    'descripcion': desc, 'resultado': 'conforme',
                    'observaciones': 'Cumple requisitos',
                }
            )

        insp2, _ = Inspeccion.objects.get_or_create(
            empresa=emp, centro_trabajo=c3, fecha_inspeccion=date(2025, 2, 10),
            defaults={
                'plantilla': plantilla, 'inspector': tech, 'estado': 'con_nc',
                'resultado_general': 'parcial', 'observaciones': 'Detectadas 2 no conformidades menores',
                'nc_generadas': True, 'creado_por': admin,
            }
        )
        self.stdout.write(f'  Inspecciones: 1 plantilla, 2 inspecciones')

        # ── Incidentes / Accidentes ──
        from apps.incidents.models import Accidente, Incidente, CausaAccidente
        causa1, _ = CausaAccidente.objects.get_or_create(
            empresa=emp, nombre='Falta de EPI', defaults={'categoria': 'inmediata', 'activa': True}
        )
        causa2, _ = CausaAccidente.objects.get_or_create(
            empresa=emp, nombre='Deficiencia formativa', defaults={'categoria': 'basica', 'activa': True}
        )

        Accidente.objects.get_or_create(
            empresa=emp, codigo='ACC-AL-001',
            defaults={
                'titulo': 'Corte leve en manipulación de chapa',
                'fecha': timezone.now() - timedelta(days=180),
                'centro_trabajo': c1, 'ubicacion': 'Zona de corte', 'tipo': 'trabajo',
                'gravedad': 'sin_baja', 'tipo_lesion': 'cortes', 'parte_cuerpo': 'Mano derecha',
                'descripcion': 'Corte superficial al manipular chapa sin guantes adecuados',
                'estado': 'cerrado', 'creado_por': admin,
            }
        )
        for i in range(3):
            Incidente.objects.get_or_create(
                empresa=emp, codigo=f'INC-AL-{i+1:03d}',
                defaults={
                    'titulo': random.choice(['Casi-caída de altura', 'Protección máquina dañada', 'Fuga químico menor']),
                    'fecha': timezone.now() - timedelta(days=random.randint(30, 300)),
                    'centro_trabajo': random.choice([c1, c2]),
                    'descripcion': 'Incidente sin lesión investigado y resuelto',
                    'potencial_dano': random.choice(['leve', 'moderada']),
                    'gravedad_potencial': 'leve', 'estado': 'cerrado', 'creado_por': admin,
                }
            )
        self.stdout.write('  Incidentes/Accidentes: 1 accidente cerrado, 3 incidentes cerrados')

        # ── No Conformidades ──
        from apps.corrective_actions.models import NoConformidad, AccionCorrectiva
        nc1, _ = NoConformidad.objects.get_or_create(
            empresa=emp, codigo='NC-AL-001',
            defaults={
                'titulo': 'Extintor sin revisar en zona B', 'gravedad': 'moderada', 'estado': 'cerrada',
                'descripcion': 'El extintor de la zona B lleva sin revisar 8 meses',
                'fuente': 'inspeccion', 'detectado_por': admin, 'fecha_deteccion': date(2024, 9, 1),
                'centro_trabajo': c1, 'fecha_limite_resolucion': date(2024, 9, 15),
                'resuelta_en': date(2024, 9, 10), 'verificada': True,
                'fecha_verificacion': date(2024, 9, 12), 'verificada_por': admin, 'creado_por': admin,
            }
        )
        AccionCorrectiva.objects.get_or_create(
            no_conformidad=nc1, descripcion='Revisión completa de extintores zona B',
            defaults={'responsable': admin, 'fecha_limite': date(2024, 9, 15),
                       'estado': 'completada', 'fecha_ejecucion': date(2024, 9, 10)}
        )
        nc2, _ = NoConformidad.objects.get_or_create(
            empresa=emp, codigo='NC-AL-002',
            defaults={
                'titulo': 'Señalización deteriorada pasillo norte', 'gravedad': 'menor', 'estado': 'cerrada',
                'descripcion': 'Señales de salida de emergencia deterioradas',
                'fuente': 'interna', 'detectado_por': tech, 'fecha_deteccion': date(2024, 10, 5),
                'centro_trabajo': c1, 'fecha_limite_resolucion': date(2024, 10, 20),
                'resuelta_en': date(2024, 10, 15), 'verificada': True,
                'fecha_verificacion': date(2024, 10, 17), 'verificada_por': admin, 'creado_por': admin,
            }
        )
        AccionCorrectiva.objects.get_or_create(
            no_conformidad=nc2, descripcion='Sustitución de señalización deteriorada',
            defaults={'responsable': tech, 'fecha_limite': date(2024, 10, 20),
                       'estado': 'completada', 'fecha_ejecucion': date(2024, 10, 14)}
        )
        self.stdout.write('  No Conformidades: 2 cerradas con acciones correctivas')

        # ── EPIs ──
        from apps.epis.models import CatalogoEPI, EPI, EntregaEPI, InspeccionEPI
        catalogs = []
        for nombre, cat, norma in [
            ('Casco de seguridad', 'cabeza', 'EN 397'), ('Guantes de protección', 'manos', 'EN 388'),
            ('Calzado de seguridad', 'pies', 'EN ISO 20345'), ('Gafas de protección', 'ojos', 'EN 166'),
            ('Protección auditiva', 'oidos', 'EN 352'), ('Arnés de seguridad', 'cuerpo', 'EN 361'),
        ]:
            c, _ = CatalogoEPI.objects.get_or_create(
                nombre=nombre, defaults={'categoria': cat, 'riesgos_proteccion': nombre, 'norma_eu': norma}
            )
            catalogs.append(c)

        epi_count = 0
        for cat in catalogs:
            epi, _ = EPI.objects.get_or_create(
                empresa=emp, catalogo=cat, marca='MSA', modelo='Standard',
                numero_serie=f'EP-AL-{random.randint(1000, 9999)}',
                defaults={'estado': 'asignado', 'fecha_compra': date(2024, 1, 1)}
            )
            for trab in random.sample(t[:6], min(3, 6)):
                e, _ = EntregaEPI.objects.get_or_create(
                    empresa=emp, epi=epi, trabajador=trab, fecha_entrega=date(2024, 3, 1),
                    defaults={'estado': 'activo', 'entregado_por': admin}
                )
                InspeccionEPI.objects.get_or_create(
                    empresa=emp, epi=epi, fecha=date(2024, random.randint(1, 12), 15),
                    defaults={'resultado': 'bueno', 'observaciones': 'Estado correcto',
                               'inspeccionado_por': admin}
                )
            epi_count += 1
        self.stdout.write(f'  EPIs: {epi_count} catálogos con entregas e inspecciones')

        # ── Químicos ──
        from apps.chemical_products.models import ProductoQuimico, ClasificacionQuimica
        quim = 0
        for nombre, fab, uso in [
            ('Disolvente industrial Q-200', 'SolvChem', 'Disolvente orgánico multiusos'),
            ('Aceite de corte SC-50', 'LubriTech', 'Aceite para máquinas CNC'),
            ('Limpiador Industrial LI-10', 'CleanPro', 'Limpiador desengrasante'),
        ]:
            prod, _ = ProductoQuimico.objects.get_or_create(
                company=emp, nombre=nombre,
                defaults={'fabricante': fab, 'uso': uso, 'ubicacion': 'Almacén químicos',
                           'ficha_seguridad': _ph(f'Ficha de seguridad {nombre}')}
            )
            ClasificacionQuimica.objects.get_or_create(
                producto=prod, defaults={'pictograma': 'GHS02', 'frase_riesgo': 'Fácilmente inflamable'}
            )
            quim += 1
        self.stdout.write(f'  Productos químicos: {quim} con fichas de seguridad')

        # ── Vigilancia de la Salud ──
        from apps.health_surveillance.models import ReconocimientoMedico
        vs_count = 0
        for trab in t[:7]:
            ReconocimientoMedico.objects.get_or_create(
                company=emp, trabajador=trab,
                fecha=date(2024, random.randint(1, 6), random.randint(1, 28)),
                defaults={
                    'tipo': 'periodico', 'apto': True,
                    'proximo_reconocimiento': date(2025, random.randint(1, 6), random.randint(1, 28)),
                    'medico': 'Dr. Fernández - Mutual', 'file': _ph('Informe reconocimiento médico'),
                }
            )
            vs_count += 1
        self.stdout.write(f'  Vigilancia de la salud: {vs_count} reconocimientos')

        # ── Equipos de trabajo ──
        from apps.work_equipment.models import TipoEquipo, EquipoTrabajo, RevisionEquipo
        tipo_m, _ = TipoEquipo.objects.get_or_create(
            empresa=emp, nombre='Máquina CNC',
            defaults={'categoria': 'maquinaria', 'descripcion': 'Torno CNC de control numérico'}
        )
        tipo_h, _ = TipoEquipo.objects.get_or_create(
            empresa=emp, nombre='Herramienta neumática',
            defaults={'categoria': 'herramientas', 'descripcion': 'Herramientas neumáticas varias'}
        )
        eq_count = 0
        for i in range(4):
            eq, _ = EquipoTrabajo.objects.get_or_create(
                empresa=emp, tipo=tipo_m, nombre=f'CNC-{i+1:03d}',
                defaults={
                    'marca': 'DMG Mori', 'modelo': 'NLX 2500',
                    'numero_serie': f'CNC{random.randint(10000, 99999)}',
                    'estado': 'operativo', 'ubicacion': 'Fábrica - nave 1',
                    'manual_instrucciones': _ph('Manual CNC'),
                    'declaracion_ce': _ph('Declaración CE CNC'),
                    'certificado_instalacion': _ph('Certificado instalación CNC'),
                }
            )
            RevisionEquipo.objects.get_or_create(
                empresa=emp, equipo=eq, fecha=date(2024, 6, 15),
                defaults={
                    'resultado': 'conforme', 'proxima_revision': date(2025, 6, 15),
                    'observaciones': 'Estado correcto', 'realizado_por': admin,
                }
            )
            eq_count += 1
        self.stdout.write(f'  Equipos de trabajo: {eq_count} CNC con revisiones al día')

        # ── Auditorías ISO 45001 ──
        from apps.audits.models import ProgramaAuditoria, AuditoriaInterna, ChecklistAuditoria, InformeAuditoria
        prog, _ = ProgramaAuditoria.objects.get_or_create(
            empresa=emp, anio=2024,
            defaults={
                'version': '1.0', 'estado': 'completado', 'alcance': 'Cláusulas 4-10 ISO 45001',
                'aprobado_por': admin, 'fecha_aprobacion': date(2024, 1, 10),
            }
        )
        aud, _ = AuditoriaInterna.objects.get_or_create(
            empresa=emp, programa=prog, titulo='Auditoría interna Q1 2024',
            defaults={
                'descripcion': 'Auditoría completa del SM-SST', 'fecha_planificada': date(2024, 3, 20),
                'fecha_realizacion': date(2024, 3, 20), 'lider_auditoria': tech, 'estado': 'cerrada',
            }
        )
        aud.equipo_auditor.add(tech, admin)
        clausulas = [
            ('4.1', 'Contexto', 'Comprensión de la organización', 'conforme'),
            ('4.2', 'Contexto', 'Partes interesadas', 'conforme'),
            ('5.1', 'Liderazgo', 'Liderazgo y compromiso', 'conforme'),
            ('5.2', 'Liderazgo', 'Política de SST', 'conforme'),
            ('6.1', 'Planificación', 'Acciones para abordar riesgos', 'observacion'),
            ('7.1', 'Apoyo', 'Recursos', 'conforme'),
            ('7.2', 'Apoyo', 'Competencia', 'conforme'),
            ('8.1', 'Operación', 'Planificación operativa', 'conforme'),
            ('8.2', 'Operación', 'Emergencias', 'conforme'),
            ('9.1', 'Evaluación', 'Seguimiento y medición', 'observacion'),
            ('9.2', 'Evaluación', 'Auditoría interna', 'conforme'),
            ('10.1', 'Mejora', 'No conformidad y acción correctiva', 'conforme'),
        ]
        for cl, sec, req, conf in clausulas:
            ChecklistAuditoria.objects.get_or_create(
                auditoria=aud, clausula_iso=cl,
                defaults={
                    'seccion': sec, 'requisito': req, 'conformidad': conf,
                    'evidencia_encontrada': 'Evidencia verificada on-site',
                }
            )
        InformeAuditoria.objects.get_or_create(
            auditoria=aud,
            defaults={
                'resumen_ejecutivo': 'Auditoría satisfactoria con 2 observaciones menores',
                'hallazgos_resumen': '2 observaciones en cláusulas 6.1 y 9.1',
                'puntos_fuertes': 'Liderazgo comprometido, formación actualizada',
                'oportunidades_mejora': 'Mejorar seguimiento de indicadores de prevención',
                'recomendaciones': 'Implementar cuadro de mando de indicadores PRL',
                'fecha_informe': date(2024, 3, 25), 'elaborado_por': tech, 'aprobado_por': admin,
                'fecha_aprobacion': date(2024, 3, 28),
            }
        )
        self.stdout.write('  Auditorías: 1 programa, 1 auditoría cerrada, 12 items, informe')

        # ── Cumplimiento Legal ──
        from apps.legal_requirements.models import CumplimientoLegal
        for req in self._requisitos_legales[:10]:
            CumplimientoLegal.objects.get_or_create(
                empresa=emp, requisito=req,
                defaults={
                    'estado': random.choice(['cumple', 'cumple', 'cumple', 'en_curso']),
                    'evaluado_por': tech, 'fecha_evaluacion': date(2024, random.randint(1, 12), 15),
                    'fecha_proxima_revision': date(2025, random.randint(1, 12), 15),
                    'responsable': tech, 'evidencia': 'Documentación revisada y verificada',
                }
            )
        self.stdout.write(f'  Cumplimiento Legal: 10 requisitos (mayoría cumple)')

        # ── Instrucciones de Trabajo ──
        from apps.work_instructions.models import InstruccionTrabajo
        for i, puesto in enumerate([p0, p1, p2, p3, p4], 1):
            InstruccionTrabajo.objects.get_or_create(
                company=emp, codigo=f'IT-{i:03d}',
                defaults={
                    'titulo': f'Instrucción de trabajo para {puesto.name}',
                    'puesto_trabajo': puesto, 'activo': True,
                    'contenido': f'Procedimiento estándar para {puesto.name}. Normas de seguridad, EPIs y protocolo de emergencia.',
                    'file': _ph(f'IT {puesto.name}'),
                }
            )
        self.stdout.write('  Instrucciones de trabajo: 5')

        # ── CAE (Coordinación de Actividades Empresariales) ──
        from apps.cae.models import EmpresaSubcontrata, DocumentoCAETipo, DocumentoCAE, ProcedimientoCAE
        doc_tipos = []
        for nombre in ['Certificado de empresa', 'Política de prevención', 'Evaluación de riesgos', 'Justificante formación']:
            dt, _ = DocumentoCAETipo.objects.get_or_create(
                nombre=nombre, defaults={'obligatorio': True, 'activo': True}
            )
            doc_tipos.append(dt)

        sub1, _ = EmpresaSubcontrata.objects.get_or_create(
            empresa=emp, nombre_empresa='Electricidad del Sur S.L.',
            defaults={
                'trabajo_realizar': 'Mantenimiento eléctrico periódico',
                'persona_contacto': 'Antonio López', 'telefono': '915551234',
                'email': 'antonio@elecsur-test.com', 'activa': True,
            }
        )
        for dt in doc_tipos[:2]:
            DocumentoCAE.objects.get_or_create(
                empresa_subcontrata=sub1, tipo_documento=dt,
                defaults={
                    'documento': _ph(f'Doc CAE: {dt.nombre} - Electricidad del Sur'),
                    'fecha_subida': timezone.now(), 'fecha_caducidad': date(2025, 12, 31),
                }
            )

        sub2, _ = EmpresaSubcontrata.objects.get_or_create(
            empresa=emp, nombre_empresa='Limpiezas Express S.A.',
            defaults={
                'trabajo_realizar': 'Limpieza de naves industriales',
                'persona_contacto': 'María Ruiz', 'telefono': '915559876',
                'email': 'maria@limpieza-test.com', 'activa': True,
            }
        )
        for dt in doc_tipos[:3]:
            DocumentoCAE.objects.get_or_create(
                empresa_subcontrata=sub2, tipo_documento=dt,
                defaults={
                    'documento': _ph(f'Doc CAE: {dt.nombre} - Limpiezas Express'),
                    'fecha_subida': timezone.now(), 'fecha_caducidad': date(2025, 6, 30),
                }
            )

        ProcedimientoCAE.objects.get_or_create(
            empresa=emp,
            defaults={
                'documento': _ph('Procedimiento de coordinación CAE v2.0'),
                'version': '2.0', 'fecha': date(2024, 1, 15),
            }
        )
        self.stdout.write('  CAE: 2 subcontratadas con documentación, procedimiento')

        # ── Medidas de Emergencia ──
        from apps.emergency_measures.models import (
            MedioProteccionIncendios, EmpresaMedioProteccion, PlanAutoproteccion,
            EquipoEmergencia, MiembroEquipoEmergencia, RegistroSimulacro,
        )
        for nombre in ['Extintor ABC 6kg', 'Boca de incendio', 'Manta ignífuga', 'Hidrante exterior']:
            medio, _ = MedioProteccionIncendios.objects.get_or_create(
                nombre=nombre, defaults={'activo': True}
            )
            EmpresaMedioProteccion.objects.get_or_create(
                company=emp, medio=medio,
                defaults={'cantidad': random.randint(1, 8), 'ubicacion': 'Fábrica Principal'}
            )

        PlanAutoproteccion.objects.get_or_create(
            company=emp,
            defaults={
                'file_plan': _ph('Plan de autoprotección v2.0'),
                'file_plano': _ph('Plano de evacuación fábrica'),
                'fecha_revision': date(2024, 6, 1), 'proxima_revision': date(2025, 6, 1),
            }
        )

        eq_emerg = {}
        for tipo, nombre in [
            ('jefe', 'Jefe de Emergencia'),
            ('primeros_auxilios', 'Equipo de Primeros Auxilios'),
            ('evacuacion', 'Equipo de Evacuación'),
        ]:
            eq, _ = EquipoEmergencia.objects.get_or_create(
                company=emp, tipo=tipo, nombre=nombre,
                defaults={'descripcion': f'Equipo de {nombre}'}
            )
            eq_emerg[tipo] = eq

        MiembroEquipoEmergencia.objects.get_or_create(
            equipo=eq_emerg['jefe'], trabajador=t[9],
            defaults={'rol': 'Jefe de emergencia'}
        )
        MiembroEquipoEmergencia.objects.get_or_create(
            equipo=eq_emerg['primeros_auxilios'], trabajador=t[4],
            defaults={'rol': 'Socorrista'}
        )
        MiembroEquipoEmergencia.objects.get_or_create(
            equipo=eq_emerg['evacuacion'], trabajador=t[5],
            defaults={'rol': 'Revisor de zonas'}
        )

        RegistroSimulacro.objects.get_or_create(
            company=emp, fecha=date(2024, 10, 15),
            defaults={
                'descripcion': 'Simulacro de evacuación trimestral Q4',
                'participantes': 75, 'duracion_minutos': 8,
                'observaciones': 'Evacuación completada en tiempo récord',
                'creado_por': admin,
            }
        )
        RegistroSimulacro.objects.get_or_create(
            company=emp, fecha=date(2024, 7, 10),
            defaults={
                'descripcion': 'Simulacro de incendio Q3',
                'participantes': 70, 'duracion_minutos': 12,
                'observaciones': 'Algunos trabajadores necesitaron refresher',
                'creado_por': admin,
            }
        )
        self.stdout.write('  Emergencias: plan, 4 medios, 3 equipos, 2 simulacros')

        # ── Planificación Preventiva ──
        from apps.preventive_planning.models import ItemPlanificacion
        items_plan = [
            ('evitables', 'Caída de objetos en almacén', 'Instalar redes anti-caída', 'implementada', 'Alto'),
            ('no_evitables', 'Ruido en zona CNC', 'Reducción de ruido en origen', 'implementada', 'Medio'),
            ('monitorizables', 'Exposición a productos químicos', 'Ventilación y EPIs', 'implementada', 'Alto'),
            ('evitables', 'Resbalones en zona de carga', 'Suelo antideslizante y señalización', 'en_curso', 'Medio'),
            ('no_evitables', 'Esfuerzos repetitivos', 'Programa de ergonomía', 'continua', 'Bajo'),
        ]
        for tipo, factor, medida, estado, resp in items_plan:
            ItemPlanificacion.objects.get_or_create(
                empresa=emp, factor_riesgo=factor,
                defaults={
                    'evaluacion_riesgos': ev,
                    'ambito_puesto': 'Fábrica Principal',
                    'tipo_factor_riesgo': tipo,
                    'medidas_preventivas': medida, 'estado': estado,
                    'responsable': resp,
                    'riesgos': 'atrapamientos' if tipo == 'evitables' else 'ergonomico',
                    'pb': 'A', 'sv': 'M', 'gr': 'A',
                }
            )
        self.stdout.write('  Planificación preventiva: 5 items')

        # ── Enfermedad Profesional ──
        from apps.epps.models import EnfermedadProfesional, InvestigacionEEPP
        ep, _ = EnfermedadProfesional.objects.get_or_create(
            empresa=emp, codigo='EP-AL-001',
            defaults={
                'titulo': 'Hipoacusia por ruido', 'fecha_diagnostico': date(2024, 3, 10),
                'centro_trabajo': c1, 'trabajador_afectado': t[1],
                'nombre_enfermedad': 'Hipoacusia neurosensorial bilateral',
                'agente_causante': 'fisico', 'tipo_exposicion': 'Ruido continuo en zona CNC',
                'duracion_exposicion': '5 años', 'parte_cuerpo': 'Oído bilateral',
                'gravedad': 'leve', 'descripcion': 'Pérdida auditiva leve por exposición prolongada a ruido',
                'estado': 'cerrado', 'creado_por': admin,
            }
        )
        InvestigacionEEPP.objects.get_or_create(
            enfermedad=ep,
            defaults={
                'fecha_inicio': date(2024, 3, 15), 'metodologia': '_5_porques',
                'puesto_trabajo': 'Operario CNC', 'riesgo_identificado': 'sordera_ruido',
                'medidas_preventivas': 'Reducción ruido y protección auditiva',
                'conclusiones': 'Exposición crónica sin protección auditiva adecuada',
                'estado': 'completada', 'investigador': admin,
            }
        )
        self.stdout.write('  Enfermedades profesionales: 1 registrada e investigada')

        # ── Tareas y Alertas ──
        from apps.tasks.models import Task, Alert
        Task.objects.get_or_create(
            company=emp, title='Revisión anual de extintores',
            defaults={
                'description': 'Programar revisión anual de todos los extintores',
                'priority': 'high', 'assigned_to': tech, 'created_by': admin,
                'due_date': date(2025, 3, 1), 'status': 'pending',
            }
        )
        Task.objects.get_or_create(
            company=emp, title='Actualizar plan de prevención',
            defaults={
                'description': 'Revisar y actualizar el plan de prevención anual',
                'priority': 'medium', 'assigned_to': admin, 'created_by': admin,
                'due_date': date(2025, 1, 31), 'status': 'completed',
                'completed_at': timezone.now() - timedelta(days=30),
            }
        )
        Alert.objects.get_or_create(
            company=emp, title='Vencimiento reconocimiento médico',
            defaults={
                'message': '5 trabajadores con reconocimiento médico próximo a vencer',
                'alert_type': 'health_surveillance', 'severity': 'warning',
                'due_date': date(2025, 6, 30),
            }
        )
        self.stdout.write('  Tareas/Alertas: 2 tareas, 1 alerta')

        self.stdout.write(self.style.SUCCESS(f'  [OK] Empresa A completa\n'))

    # ══════════════════════════════════════════════════════════════════════
    #  EMPRESA B — GRUPO NORTE LOGÍSTICA S.A. (COMPLETA)
    # ══════════════════════════════════════════════════════════════════════
    def _crear_empresa_b(self, u):
        self.stdout.write(self.style.MIGRATE_HEADING(
            '\n-- EMPRESA B: Grupo Norte Logistica S.A. (COMPLETA) --'
        ))
        emp = self._empresa(
            'A12345678', 'Grupo Norte Logística S.A.', 'Norte Logística',
            email='info@norte-test.com', phone='944123456',
            address='Avda. del Progreso, 100', postal_code='48013',
            city='Bilbao', province='Vizcaya', ac='País Vasco',
            activity='Almacenaje y distribución logística', cnae='5210', workforce=120,
        )
        admin, tech = u['laura_norte'], u['carlos_tecnico']
        self._membresia(admin, emp, 'company_admin', True)
        self._membresia(tech, emp, 'technician')
        self._membresia(u['admin_test'], emp, 'company_admin', False)

        # ── Centros de trabajo ──
        c1 = self._centro(emp, name='Centro Logístico Principal', code='CL-001',
                          address='Avda. Progreso 100', postal_code='48013', city='Bilbao',
                          province='Vizcaya', activity='Almacenaje y carga', workers=80, risk='high')
        c2 = self._centro(emp, name='Plataforma de Distribución', code='PD-001',
                          address='Polígona Gallarta, 5', postal_code='48499', city='Ugao-Miraballes',
                          province='Vizcaya', activity='Distribución', workers=40, risk='medium')

        # ── Puestos ──
        p0 = self._puesto(emp, 'Encargado de Almacén', 'Operaciones')
        p1 = self._puesto(emp, 'Operario de Almacén', 'Operaciones')
        p2 = self._puesto(emp, 'Conductor de Carretilla', 'Logística')
        p3 = self._puesto(emp, 'Preparador de Pedidos', 'Operaciones')
        p4 = self._puesto(emp, 'Técnico de Mantenimiento', 'Mantenimiento')
        p5 = self._puesto(emp, 'Administrativo de Logística', 'Administración')

        # ── Trabajadores ──
        t = []
        for fn, ln, nif, centro, puesto in [
            ('Iker', 'Etxeberria Goikoetxea', '48123456A', c1, p0),
            ('Ane', 'Zubíaurre López', '48234567B', c1, p1),
            ('Gorka', 'Aguirre Mendizabal', '48345678C', c1, p2),
            ('Nerea', 'Bilbao Guerra', '48456789D', c1, p3),
            ('Unai', 'López de Uralde', '48567890E', c2, p2),
            ('Miren', 'Elosegi Zabala', '48678901F', c2, p3),
            ('Aitor', 'Uriarte Gallastegi', '48789012G', c1, p4),
            ('Leire', 'Zubiaga Arana', '48890123H', c2, p5),
        ]:
            t.append(self._trabajador(emp, fn, ln, nif, centro, puesto))
        self.stdout.write(f'  Centros: 2 | Puestos: 6 | Trabajadores: {len(t)}')

        # ── Plan de Prevención ──
        from apps.prevention_plan.models import PlanPrevention
        PlanPrevention.objects.get_or_create(
            company=emp,
            defaults={
                'politica_firmada': True,
                'delegado_prl': 'si', 'delegado_fecha_designacion': date(2024, 2, 1),
                'delegado_formacion': True,
                'doc_designacion_delegado': _ph('Designación delegado Norte'),
                'doc_formacion_delegado': _ph('Formación delegado Norte'),
                'recurso_preventivo': 'no_aplica',
                'organigrama_texto': 'Director Logístico → Técnico PRL → Encargados de zona',
                'funciones_responsabilidades': 'Según convenio de transporte y logística',
                'utiliza_ett': True, 'puestos_ett': 'Preparadores de pedidos en campañas',
                'tiene_teletrabajo': False,
            },
        )

        # ── Evaluación de Riesgos ──
        from apps.risk_assessment.models import TipoPeligro, EvaluacionRiesgos, ItemEvaluacionRiesgos
        peligros = []
        for cod, nombre, cat in [
            ('MEC-LOG', 'Riesgo mecánico (carretillas)', 'mecanico'),
            ('LOC-LOG', 'Riesgo locativo (caídas)', 'locativo'),
            ('ERG-LOG', 'Riesgo ergonómico (cargas)', 'ergonomico'),
            ('INC-LOG', 'Riesgo de incendio', 'incendio'),
            ('ELE-LOG', 'Riesgo eléctrico', 'electrico'),
        ]:
            p, _ = TipoPeligro.objects.get_or_create(
                codigo=cod, defaults={'nombre': nombre, 'categoria': cat, 'descripcion': nombre}
            )
            peligros.append(p)

        ev, _ = EvaluacionRiesgos.objects.get_or_create(
            empresa=emp, centro_trabajo=c1,
            titulo='Evaluación de Riesgos Centro Logístico 2024',
            defaults={
                'fecha_evaluacion': date(2024, 2, 20), 'fecha_proxima_revision': date(2025, 2, 20),
                'metodologia': 'propio', 'revisado_por': admin, 'aprobado_por': admin,
                'fecha_aprobacion': date(2024, 2, 28), 'estado': 'aprobada', 'version': '1.0',
            }
        )
        for puesto, peligro, factor, prob, sever, med in [
            (p2, peligros[0], 'Conducción carretilla', 2, 3, 'Formación, casco, chaleco'),
            (p1, peligros[2], 'Manipulación de carga', 2, 2, 'Ayudas mecánicas, formación'),
            (p3, peligros[1], 'Picking en estantería', 2, 2, 'Escaleras homologadas, calzado'),
            (p0, peligros[3], 'Zona de almacén', 1, 3, 'Extintores, planes de emergencia'),
        ]:
            ItemEvaluacionRiesgos.objects.get_or_create(
                evaluacion=ev, puesto_trabajo=puesto, tipo_peligro=peligro,
                defaults={
                    'tipo_riesgo': 'no_evitable', 'factor_riesgo_condicion': factor,
                    'medidas_existentes': med, 'probabilidad': prob, 'severidad': sever,
                    'medidas_propuestas': f'Mejorar {med.lower()}',
                    'estado_implementacion': 'implementada',
                }
            )

        # ── Formación ──
        from apps.training.models import TrainingCategory, TrainingCourse, TrainingRecord
        cat_b, _ = TrainingCategory.objects.get_or_create(
            name='Formación Básica', defaults={'code': 'FB-NOR', 'description': 'Básica'}
        )
        cat_e, _ = TrainingCategory.objects.get_or_create(
            name='Operaciones', defaults={'code': 'OP-NOR', 'description': 'Operaciones de almacén'}
        )
        cursos = []
        for cat, nombre, horas, code in [
            (cat_b, 'PRL Básica Logística', 6, 'FB-NOR-001'),
            (cat_e, 'Operación de Carretillas Elevadoras', 8, 'OP-NOR-001'),
            (cat_e, 'Trabajo Seguro en Almacén', 4, 'OP-NOR-002'),
            (cat_b, 'Primeros Auxilios', 16, 'FB-NOR-002'),
        ]:
            c, _ = TrainingCourse.objects.get_or_create(
                company=emp, name=nombre,
                defaults={
                    'category': cat, 'duration_hours': horas, 'is_mandatory': True,
                    'requires_renewal': horas > 6, 'modality': 'presential',
                    'validity_value': 12 if horas > 6 else None,
                    'validity_unit': 'months' if horas > 6 else '', 'status': 'active',
                    'code': code,
                }
            )
            cursos.append(c)

        reg_count = 0
        for trab in t[:6]:
            for curso in random.sample(cursos, min(3, len(cursos))):
                if random.random() > 0.2:
                    TrainingRecord.objects.get_or_create(
                        company=emp, worker=trab, course=curso,
                        completed_date=date(2024, random.randint(1, 12), random.randint(1, 28)),
                        defaults={'status': 'completed', 'created_by': admin}
                    )
                    reg_count += 1
        self.stdout.write(f'  Formación: {len(cursos)} cursos, {reg_count} registros')

        # ── Documentos ──
        cats_doc = {}
        for nombre, slug, oblig in [
            ('Plan de Prevención', 'plan-prevencion', True),
            ('Evaluación de Riesgos', 'evaluacion-riesgos', True),
            ('Protocolo de Emergencia', 'emergencias', True),
            ('Procedimiento de Trabajo Seguro', 'procedimientos', True),
            ('Política de Formación', 'formacion', False),
            ('Registro de EPIs', 'epis', True),
        ]:
            cats_doc[slug] = self._doc_cat(nombre, slug, oblig)

        for slug, titulo, code, desc in [
            ('plan-prevencion', 'Plan Prevención Norte 2024', 'PP-NOR-001', 'Plan completo de prevención'),
            ('evaluacion-riesgos', 'Evaluación Riesgos Almacén', 'ER-NOR-001', 'Evaluación completa del almacén'),
            ('emergencias', 'Protocolo Emergencia Logística', 'EM-NOR-001', 'Protocolo de emergencias almacén'),
            ('procedimientos', 'PTO Conducción Carretillas', 'PT-NOR-001', 'Procedimiento seguro de conducción'),
            ('procedimientos', 'PTO Picking Seguro', 'PT-NOR-002', 'Procedimiento de preparación de pedidos'),
            ('formacion', 'Plan Formación Norte 2024', 'PF-NOR-001', 'Plan anual de formación'),
            ('epis', 'Inventario EPIs Norte', 'EP-NOR-001', 'Inventario actualizado'),
            ('epis', 'Registro Entregas EPIs', 'EP-NOR-002', 'Control de entregas'),
        ]:
            self._documento(emp, cats_doc[slug], titulo, admin, code=code, desc=desc)
        self.stdout.write(f'  Documentos: 8')

        # ── Inspecciones ──
        from apps.inspections.models import PlantillaInspeccion, PlantillaInspeccionItem, Inspeccion
        plantilla, _ = PlantillaInspeccion.objects.get_or_create(
            empresa=emp, nombre='Inspección Almacén Logístico',
            defaults={'categoria': 'seguridad', 'descripcion': 'Inspección de seguridad en almacén'}
        )
        for i, desc in enumerate([
            'Estanterías en buen estado', 'Pasillos libres de obstáculos',
            'Extintores accesibles', 'Señalización completa', 'Carretillas en buen estado',
        ], 1):
            PlantillaInspeccionItem.objects.get_or_create(
                plantilla=plantilla, orden=i, defaults={'descripcion': desc}
            )

        Inspeccion.objects.get_or_create(
            empresa=emp, centro_trabajo=c1, fecha_inspeccion=date(2024, 8, 20),
            defaults={
                'plantilla': plantilla, 'inspector': admin, 'estado': 'completada',
                'resultado_general': 'conforme', 'creado_por': admin,
            }
        )
        Inspeccion.objects.get_or_create(
            empresa=emp, centro_trabajo=c1, fecha_inspeccion=date(2025, 1, 15),
            defaults={
                'plantilla': plantilla, 'inspector': tech, 'estado': 'con_nc',
                'resultado_general': 'parcial', 'nc_generadas': True, 'creado_por': admin,
            }
        )
        self.stdout.write('  Inspecciones: 1 plantilla, 2 inspecciones')

        # ── Incidentes / Accidentes ──
        from apps.incidents.models import Accidente, Incidente, InvestigacionAccidente
        Accidente.objects.get_or_create(
            empresa=emp, codigo='ACC-GL-001',
            defaults={
                'titulo': 'Caída de mercancía de estantería baja',
                'fecha': timezone.now() - timedelta(days=120),
                'centro_trabajo': c1, 'ubicacion': 'Zona de picking',
                'tipo': 'trabajo', 'gravedad': 'baja_temporal',
                'tipo_lesion': 'contusiones', 'parte_cuerpo': 'Tobillo derecho',
                'descripcion': 'Trabajador golpeado por caja que cae de estantería a 1.5m',
                'estado': 'cerrado', 'creado_por': admin,
            }
        )
        Accidente.objects.get_or_create(
            empresa=emp, codigo='ACC-GL-002',
            defaults={
                'titulo': 'Atropellamiento leve con carretilla',
                'fecha': timezone.now() - timedelta(days=45),
                'centro_trabajo': c2, 'ubicacion': 'Pasillo principal',
                'tipo': 'trabajo', 'gravedad': 'sin_baja',
                'tipo_lesion': 'contusiones', 'parte_cuerpo': 'Pierna izquierda',
                'descripcion': 'Golpe leve por carretilla en pasillo',
                'estado': 'cerrado', 'creado_por': admin,
            }
        )
        Incidente.objects.get_or_create(
            empresa=emp, codigo='INC-GL-001',
            defaults={
                'titulo': 'Estantería con cargamento inestable',
                'fecha': timezone.now() - timedelta(days=60),
                'centro_trabajo': c1, 'descripcion': 'Estantería con exceso de carga detectada',
                'potencial_dano': 'grave', 'gravedad_potencial': 'grave',
                'estado': 'cerrado', 'creado_por': admin,
            }
        )
        Incidente.objects.get_or_create(
            empresa=emp, codigo='INC-GL-002',
            defaults={
                'titulo': 'Fuga de producto en zona de carga',
                'fecha': timezone.now() - timedelta(days=20),
                'centro_trabajo': c1, 'descripcion': 'Fuga de producto corrosivo sin identificar',
                'potencial_dano': 'moderada', 'gravedad_potencial': 'moderada',
                'estado': 'en_estudio', 'creado_por': admin,
            }
        )
        self.stdout.write('  Incidentes/Accidentes: 2 accidentes cerrados, 2 incidentes (1 cerrado, 1 en estudio)')

        # ── No Conformidades ──
        from apps.corrective_actions.models import NoConformidad, AccionCorrectiva
        nc1, _ = NoConformidad.objects.get_or_create(
            empresa=emp, codigo='NC-GL-001',
            defaults={
                'titulo': 'Estantería dañada sin reparar', 'gravedad': 'moderada', 'estado': 'cerrada',
                'descripcion': 'Estantería con pieza doblada sin reparar desde hace 3 meses',
                'fuente': 'inspeccion', 'detectado_por': admin, 'fecha_deteccion': date(2024, 8, 20),
                'centro_trabajo': c1, 'fecha_limite_resolucion': date(2024, 9, 1),
                'resuelta_en': date(2024, 8, 28), 'verificada': True,
                'fecha_verificacion': date(2024, 8, 30), 'verificada_por': admin, 'creado_por': admin,
            }
        )
        AccionCorrectiva.objects.get_or_create(
            no_conformidad=nc1, descripcion='Reparación de estantería dañada',
            defaults={'responsable': admin, 'fecha_limite': date(2024, 9, 1),
                       'estado': 'completada', 'fecha_ejecucion': date(2024, 8, 28)}
        )
        nc2, _ = NoConformidad.objects.get_or_create(
            empresa=emp, codigo='NC-GL-002',
            defaults={
                'titulo': 'EPI caducado en uso', 'gravedad': 'importante', 'estado': 'en_tratamiento',
                'descripcion': 'Trabajador usando guantes caducados',
                'fuente': 'interna', 'detectado_por': tech, 'fecha_deteccion': date(2025, 1, 15),
                'centro_trabajo': c1, 'fecha_limite_resolucion': date(2025, 2, 1),
                'creado_por': admin,
            }
        )
        AccionCorrectiva.objects.get_or_create(
            no_conformidad=nc2, descripcion='Sustituir guantes y revisar sistema de control',
            defaults={'responsable': tech, 'fecha_limite': date(2025, 2, 1), 'estado': 'en_progreso'}
        )
        self.stdout.write('  No Conformidades: 1 cerrada, 1 en tratamiento')

        # ── EPIs ──
        from apps.epis.models import CatalogoEPI, EPI, EntregaEPI
        catalogs = []
        for nombre, cat, norma in [
            ('Casco de seguridad', 'cabeza', 'EN 397'),
            ('Guantes anticorte', 'manos', 'EN 388'),
            ('Chaleco reflectante', 'cuerpo', 'EN ISO 20471'),
            ('Calzado de seguridad', 'pies', 'EN ISO 20345'),
        ]:
            c, _ = CatalogoEPI.objects.get_or_create(
                nombre=nombre, defaults={'categoria': cat, 'riesgos_proteccion': nombre, 'norma_eu': norma}
            )
            catalogs.append(c)

        epi_count = 0
        for cat in catalogs:
            epi, _ = EPI.objects.get_or_create(
                empresa=emp, catalogo=cat, marca='3M', modelo='Industrial',
                numero_serie=f'EP-GL-{random.randint(1000, 9999)}',
                defaults={'estado': 'asignado', 'fecha_compra': date(2024, 2, 1)}
            )
            for trab in random.sample(t[:6], min(4, 6)):
                EntregaEPI.objects.get_or_create(
                    empresa=emp, epi=epi, trabajador=trab, fecha_entrega=date(2024, 3, 1),
                    defaults={'estado': 'activo', 'entregado_por': admin}
                )
            epi_count += 1
        self.stdout.write(f'  EPIs: {epi_count} catálogos con entregas')

        # ── Químicos ──
        from apps.chemical_products.models import ProductoQuimico, ClasificacionQuimica
        for nombre, fab, uso in [
            ('Aceite hidráulico AH-100', 'HydroLube', 'Mantenimiento carretillas'),
            ('Limpiador de suelos industrial', 'CleanMax', 'Limpieza de suelo almacén'),
        ]:
            prod, _ = ProductoQuimico.objects.get_or_create(
                company=emp, nombre=nombre,
                defaults={'fabricante': fab, 'uso': uso, 'ubicacion': 'Almacén mantenimiento',
                           'ficha_seguridad': _ph(f'Ficha seguridad {nombre}')}
            )
            ClasificacionQuimica.objects.get_or_create(
                producto=prod, defaults={'pictograma': 'GHS07', 'frase_riesgo': 'Irritante'}
            )
        self.stdout.write('  Productos químicos: 2 con fichas')

        # ── Vigilancia de la Salud ──
        from apps.health_surveillance.models import ReconocimientoMedico
        for trab in t[:5]:
            ReconocimientoMedico.objects.get_or_create(
                company=emp, trabajador=trab,
                fecha=date(2024, random.randint(1, 6), random.randint(1, 28)),
                defaults={
                    'tipo': 'periodico', 'apto': True,
                    'proximo_reconocimiento': date(2025, random.randint(1, 6), random.randint(1, 28)),
                    'medico': 'Dra. Bilbao - Medicina del Trabajo',
                }
            )
        self.stdout.write('  Vigilancia de la salud: 5 reconocimientos')

        # ── Equipos de trabajo ──
        from apps.work_equipment.models import TipoEquipo, EquipoTrabajo, RevisionEquipo
        tipo_c, _ = TipoEquipo.objects.get_or_create(
            empresa=emp, nombre='Carretilla elevadora',
            defaults={'categoria': 'elevacion', 'descripcion': 'Carretilla elevadora diésel'}
        )
        tipo_r, _ = TipoEquipo.objects.get_or_create(
            empresa=emp, nombre='Transpaleta eléctrica',
            defaults={'categoria': 'elevacion', 'descripcion': 'Transpaleta eléctrica'}
        )
        for i in range(3):
            eq, _ = EquipoTrabajo.objects.get_or_create(
                empresa=emp, tipo=tipo_c, nombre=f'Carretilla-{i+1}',
                defaults={
                    'marca': 'Toyota', 'modelo': '8FBN25',
                    'numero_serie': f'CAR{random.randint(10000, 99999)}',
                    'estado': 'operativo', 'ubicacion': 'Centro Logístico',
                    'manual_instrucciones': _ph('Manual carretilla'),
                    'declaracion_ce': _ph('Declaración CE'),
                }
            )
            RevisionEquipo.objects.get_or_create(
                empresa=emp, equipo=eq, fecha=date(2024, random.randint(3, 10), 15),
                defaults={
                    'resultado': 'conforme', 'proxima_revision': date(2025, random.randint(3, 10), 15),
                    'realizado_por': admin,
                }
            )
        for i in range(2):
            EquipoTrabajo.objects.get_or_create(
                empresa=emp, tipo=tipo_r, nombre=f'Transpaleta-{i+1}',
                defaults={
                    'marca': 'Still', 'modelo': 'EXV-SF',
                    'numero_serie': f'TR{random.randint(10000, 99999)}',
                    'estado': 'operativo', 'ubicacion': 'Centro Logístico',
                }
            )
        self.stdout.write('  Equipos: 3 carretillas con revisiones, 2 transpaletas')

        # ── Auditorías ISO 45001 ──
        from apps.audits.models import ProgramaAuditoria, AuditoriaInterna, ChecklistAuditoria
        prog, _ = ProgramaAuditoria.objects.get_or_create(
            empresa=emp, anio=2024,
            defaults={
                'version': '1.0', 'estado': 'completado', 'alcance': 'Cláusulas 4-10 ISO 45001',
                'aprobado_por': admin, 'fecha_aprobacion': date(2024, 1, 20),
            }
        )
        aud, _ = AuditoriaInterna.objects.get_or_create(
            empresa=emp, programa=prog, titulo='Auditoría Logística Q2 2024',
            defaults={
                'descripcion': 'Auditoría del SM-SST en entorno logístico',
                'fecha_planificada': date(2024, 6, 15), 'fecha_realizacion': date(2024, 6, 18),
                'lider_auditoria': tech, 'estado': 'cerrada',
            }
        )
        aud.equipo_auditor.add(tech)
        for cl, sec, req, conf in [
            ('4.1', 'Contexto', 'Análisis del contexto', 'conforme'),
            ('5.1', 'Liderazgo', 'Compromiso dirección', 'conforme'),
            ('6.1', 'Planificación', 'Riesgos y oportunidades', 'observacion'),
            ('7.2', 'Apoyo', 'Competencia del personal', 'conforme'),
            ('8.1', 'Operación', 'Control operativo', 'observacion'),
            ('8.2', 'Operación', 'Preparación ante emergencias', 'conforme'),
            ('9.1', 'Evaluación', 'Seguimiento y medición', 'conforme'),
            ('10.1', 'Mejora', 'Acción correctiva', 'conforme'),
        ]:
            ChecklistAuditoria.objects.get_or_create(
                auditoria=aud, clausula_iso=cl,
                defaults={
                    'seccion': sec, 'requisito': req, 'conformidad': conf,
                    'evidencia_encontrada': 'Revisión in situ',
                }
            )
        self.stdout.write('  Auditorías: 1 programa, 1 auditoría cerrada, 8 items checklist')

        # ── Cumplimiento Legal ──
        from apps.legal_requirements.models import CumplimientoLegal
        for req in self._requisitos_legales[:8]:
            CumplimientoLegal.objects.get_or_create(
                empresa=emp, requisito=req,
                defaults={
                    'estado': random.choice(['cumple', 'cumple', 'en_curso']),
                    'evaluado_por': tech, 'fecha_evaluacion': date(2024, random.randint(1, 12), 15),
                    'fecha_proxima_revision': date(2025, random.randint(1, 12), 15),
                    'responsable': tech,
                }
            )
        self.stdout.write(f'  Cumplimiento Legal: 8 requisitos evaluados')

        # ── Instrucciones de Trabajo ──
        from apps.work_instructions.models import InstruccionTrabajo
        for i, puesto in enumerate([p0, p1, p2, p3], 1):
            InstruccionTrabajo.objects.get_or_create(
                company=emp, codigo=f'IT-NOR-{i:03d}',
                defaults={
                    'titulo': f'IT {puesto.name}',
                    'puesto_trabajo': puesto, 'activo': True,
                    'contenido': f'Procedimiento seguro para {puesto.name}',
                    'file': _ph(f'IT {puesto.name}'),
                }
            )
        self.stdout.write('  Instrucciones de trabajo: 4')

        # ── CAE ──
        from apps.cae.models import EmpresaSubcontrata, DocumentoCAETipo, DocumentoCAE
        dt, _ = DocumentoCAETipo.objects.get_or_create(
            nombre='Certificado de empresa', defaults={'obligatorio': True, 'activo': True}
        )
        sub, _ = EmpresaSubcontrata.objects.get_or_create(
            empresa=emp, nombre_empresa='Mantenimiento Industrial Vasco S.L.',
            defaults={
                'trabajo_realizar': 'Mantenimiento de carretillas y maquinaria',
                'persona_contacto': 'Iñaki Zabala', 'telefono': '944555123',
                'activa': True,
            }
        )
        DocumentoCAE.objects.get_or_create(
            empresa_subcontrata=sub, tipo_documento=dt,
            defaults={'documento': _ph('Certificado empresa MV'), 'fecha_subida': timezone.now()}
        )
        self.stdout.write('  CAE: 1 subcontratada')

        # ── Emergencia ──
        from apps.emergency_measures.models import PlanAutoproteccion, EquipoEmergencia, RegistroSimulacro
        from apps.emergency_measures.models import MedioProteccionIncendios, EmpresaMedioProteccion
        for nombre in ['Extintor ABC 6kg', 'Manta ignífuga', 'Bote de lavado de ojos']:
            medio, _ = MedioProteccionIncendios.objects.get_or_create(nombre=nombre, defaults={'activo': True})
            EmpresaMedioProteccion.objects.get_or_create(
                company=emp, medio=medio,
                defaults={'cantidad': random.randint(1, 5), 'ubicacion': 'Centro Logístico'}
            )
        PlanAutoproteccion.objects.get_or_create(
            company=emp,
            defaults={
                'file_plan': _ph('Plan autoprotección Norte'),
                'fecha_revision': date(2024, 5, 1), 'proxima_revision': date(2025, 5, 1),
            }
        )
        eq, _ = EquipoEmergencia.objects.get_or_create(
            company=emp, tipo='primeros_auxilios', nombre='Brigada Primeros Auxilios',
            defaults={'descripcion': 'Brigada de primeros auxilios del almacén'}
        )
        from apps.emergency_measures.models import MiembroEquipoEmergencia
        MiembroEquipoEmergencia.objects.get_or_create(
            equipo=eq, trabajador=t[3], defaults={'rol': 'Socorrista'}
        )
        RegistroSimulacro.objects.get_or_create(
            company=emp, fecha=date(2024, 9, 20),
            defaults={
                'descripcion': 'Simulacro de evacuación anual',
                'participantes': 100, 'duracion_minutos': 10,
                'creado_por': admin,
            }
        )
        self.stdout.write('  Emergencias: plan, 3 medios, 1 equipo, 1 simulacro')

        # ── Enfermedad Profesional ──
        from apps.epps.models import EnfermedadProfesional
        EnfermedadProfesional.objects.get_or_create(
            empresa=emp, codigo='EP-GL-001',
            defaults={
                'titulo': 'Tendinitis de hombro derecho',
                'fecha_diagnostico': date(2024, 6, 5),
                'centro_trabajo': c1, 'trabajador_afectado': t[1],
                'nombre_enfermedad': 'Tendinitis supraescapular',
                'agente_causante': 'ergonomico', 'tipo_exposicion': 'Movimientos repetitivos',
                'duracion_exposicion': '3 años', 'parte_cuerpo': 'Hombro derecho',
                'gravedad': 'leve', 'descripcion': 'Tendinitis por movimientos repetitivos en picking',
                'estado': 'cerrado', 'creado_por': admin,
            }
        )
        self.stdout.write('  Enfermedades profesionales: 1')

        # ── Tareas ──
        from apps.tasks.models import Task, Alert
        Task.objects.get_or_create(
            company=emp, title='Renovar EPIs caducados',
            defaults={
                'description': 'Sustituir guantes y calzado caducados',
                'priority': 'high', 'assigned_to': tech, 'created_by': admin,
                'due_date': date(2025, 2, 15), 'status': 'in_progress',
            }
        )
        Alert.objects.get_or_create(
            company=emp, title='Evaluación de riesgos a renovar',
            defaults={
                'message': 'La evaluación de riesgos vence en 30 días',
                'alert_type': 'document_review', 'severity': 'warning',
                'due_date': date(2025, 3, 20),
            }
        )
        self.stdout.write('  Tareas/Alertas: 1 tarea, 1 alerta')

        self.stdout.write(self.style.SUCCESS(f'  [OK] Empresa B completa\n'))

    # ══════════════════════════════════════════════════════════════════════
    #  EMPRESA C — CONSTRUCCIONES RÁPIDA SUR S.L. (~40% documentada)
    # ══════════════════════════════════════════════════════════════════════
    def _crear_empresa_c(self, u):
        self.stdout.write(self.style.MIGRATE_HEADING(
            '\n-- EMPRESA C: Construcciones Rapida Sur S.L. (DEFICIENTE ~40%) --'
        ))
        emp = self._empresa(
            'B55555555', 'Construcciones Rápida Sur S.L.', 'Rápida Sur',
            email='info@rapida-test.com', phone='954123456',
            address='Calle de la Construcción, 15', postal_code='41001',
            city='Sevilla', province='Sevilla', ac='Andalucía',
            activity='Construcción edificatoria', cnae='4120', workforce=45,
        )
        admin = u['jorge_rapida']
        self._membresia(admin, emp, 'company_admin', True)
        self._membresia(u['admin_test'], emp, 'company_admin', False)

        # ── Centros de trabajo ──
        c1 = self._centro(emp, name='Oficina Central', code='OC-RS',
                          address='C/ Construcción 15', postal_code='41001', city='Sevilla',
                          province='Sevilla', activity='Dirección y administración', workers=10, risk='low')
        c2 = self._centro(emp, name='Obra Residencial Viña Norte', code='OB-RS',
                          address='Avda. Viña Norte s/n', postal_code='41015', city='Sevilla',
                          province='Sevilla', activity='Construcción residencial', workers=35, risk='very_high')

        # ── Puestos ──
        p0 = self._puesto(emp, 'Director de Obra', 'Dirección')
        p1 = self._puesto(emp, 'Peón de Construcción', 'Operaciones')
        p2 = self._puesto(emp, 'Albañil', 'Operaciones')
        p3 = self._puesto(emp, 'Administrativo', 'Admin')

        # ── Trabajadores ──
        t = []
        for fn, ln, nif, centro, puesto in [
            ('Manuel', 'García Torres', '41111111A', c1, p0),
            ('Antonio', 'Rodríguez Cruz', '41222222B', c2, p1),
            ('José', 'Sánchez Moreno', '41333333C', c2, p2),
            ('Carmen', 'Díaz López', '41444444D', c1, p3),
            ('Francisco', 'Ramos Herrera', '41555555E', c2, p1),
        ]:
            t.append(self._trabajador(emp, fn, ln, nif, centro, puesto))
        self.stdout.write(f'  Centros: 2 | Puestos: 4 | Trabajadores: {len(t)}')

        # ── Plan de Prevención: INCOMPLETO ──
        from apps.prevention_plan.models import PlanPrevention
        PlanPrevention.objects.get_or_create(
            company=emp,
            defaults={
                'politica_firmada': False,
                'delegado_prl': 'no',
                'recurso_preventivo': 'no',
            },
        )
        self.stdout.write('  Plan de Prevención: INCOMPLETO (sin política firmada, sin delegado)')

        # ── Evaluación de Riesgos: EXPIRADA ──
        from apps.risk_assessment.models import TipoPeligro, EvaluacionRiesgos, ItemEvaluacionRiesgos
        pel, _ = TipoPeligro.objects.get_or_create(
            codigo='LOC-RS',
            defaults={'nombre': 'Caídas en obra', 'categoria': 'locativo', 'descripcion': 'Caídas a distinto nivel'}
        )
        pel2, _ = TipoPeligro.objects.get_or_create(
            codigo='MEC-RS',
            defaults={'nombre': 'Caída de objetos', 'categoria': 'mecanico', 'descripcion': 'Caída de materiales desde altura'}
        )
        ev, _ = EvaluacionRiesgos.objects.get_or_create(
            empresa=emp, centro_trabajo=c2,
            titulo='Evaluación Obra Viña Norte (2021)',
            defaults={
                'fecha_evaluacion': date(2021, 6, 1), 'fecha_proxima_revision': date(2022, 6, 1),
                'metodologia': 'propio', 'revisado_por': admin, 'estado': 'expirada', 'version': '1.0',
                'observaciones': 'Última evaluación. No se ha actualizado desde 2022.',
            }
        )
        ItemEvaluacionRiesgos.objects.get_or_create(
            evaluacion=ev, puesto_trabajo=p2, tipo_peligro=pel,
            defaults={
                'tipo_riesgo': 'no_evitable', 'factor_riesgo_condicion': 'Trabajo en andamios',
                'medidas_existentes': 'ARNÉS (no siempre usado)', 'probabilidad': 3, 'severidad': 3,
                'medidas_propuestas': '', 'estado_implementacion': 'pendiente',
            }
        )
        ItemEvaluacionRiesgos.objects.get_or_create(
            evaluacion=ev, puesto_trabajo=p1, tipo_peligro=pel2,
            defaults={
                'tipo_riesgo': 'no_evitable', 'factor_riesgo_condicion': 'Carga de materiales en altura',
                'medidas_existentes': 'Ninguna identificada', 'probabilidad': 2, 'severidad': 3,
                'medidas_propuestas': '', 'estado_implementacion': 'pendiente',
            }
        )
        self.stdout.write('  Evaluación de Riesgos: 1 EXPIRADA desde 2022, 2 items sin medidas')

        # ── Formación: MUY POCA ──
        from apps.training.models import TrainingCategory, TrainingCourse, TrainingRecord
        cat_b, _ = TrainingCategory.objects.get_or_create(
            name='Formación Básica', defaults={'code': 'FB-RS', 'description': 'Básica'}
        )
        curso, _ = TrainingCourse.objects.get_or_create(
            company=emp, name='PRL Básica (obligatoria)',
            defaults={'category': cat_b, 'duration_hours': 4, 'is_mandatory': True, 'modality': 'presential', 'status': 'active', 'code': 'FB-RS-001'}
        )
        TrainingRecord.objects.get_or_create(
            company=emp, worker=t[0], course=curso,
            completed_date=date(2022, 4, 10),
            defaults={'status': 'completed', 'created_by': admin}
        )
        TrainingRecord.objects.get_or_create(
            company=emp, worker=t[1], course=curso,
            completed_date=date(2022, 4, 10),
            defaults={'status': 'completed', 'created_by': admin}
        )
        self.stdout.write('  Formación: 1 curso, 2 registros (3 trabajadores SIN formar)')

        # ── Documentos: MUY POCA ──
        cat_doc = self._doc_cat('Plan de Prevención', 'plan-prevencion')
        self._documento(emp, cat_doc, 'Plan Prevención Básico 2021', admin,
                        status='expired', issue=date(2021, 1, 1), expiry=date(2022, 1, 1))
        self.stdout.write('  Documentos: 1 (caducado)')

        # ── Inspecciones: NINGUNA ──
        self.stdout.write('  Inspecciones: NINGUNA')

        # ── Incidentes: ABIERTOS ──
        from apps.incidents.models import Incidente, Accidente
        for i in range(3):
            Incidente.objects.get_or_create(
                empresa=emp, codigo=f'INC-RS-{i+1:03d}',
                defaults={
                    'titulo': random.choice([
                        'Caída de escombro desde andamio', 'Casi-caída de altura',
                        'Suelo resbaladizo en obra',
                    ]),
                    'fecha': timezone.now() - timedelta(days=random.randint(20, 150)),
                    'centro_trabajo': c2,
                    'descripcion': 'Sin investigación realizada',
                    'potencial_dano': random.choice(['moderada', 'grave']),
                    'gravedad_potencial': random.choice(['moderada', 'grave']),
                    'estado': 'abierto', 'creado_por': admin,
                }
            )
        Accidente.objects.get_or_create(
            empresa=emp, codigo='ACC-RS-001',
            defaults={
                'titulo': 'Caída de andamio parcial',
                'fecha': timezone.now() - timedelta(days=60),
                'centro_trabajo': c2, 'ubicacion': 'Fachada norte',
                'tipo': 'trabajo', 'gravedad': 'baja_temporal',
                'tipo_lesion': 'fracturas', 'parte_cuerpo': 'Muñeca izquierda',
                'descripcion': 'Fragmento de andamio cede, trabajador cae 2 metros',
                'estado': 'abierto', 'creado_por': admin,
            }
        )
        self.stdout.write('  Incidentes/Accidentes: 1 accidente (baja, SIN investigar), 3 incidentes (abiertos)')

        # ── No Conformidades: ABIERTAS ──
        from apps.corrective_actions.models import NoConformidad
        NoConformidad.objects.get_or_create(
            empresa=emp, codigo='NC-RS-001',
            defaults={
                'titulo': 'Falta de barandillas en plataforma de 3m', 'gravedad': 'critica',
                'estado': 'abierta', 'descripcion': 'Plataforma de trabajo a 3m sin barandillas de protección',
                'fuente': 'inspeccion', 'detectado_por': admin,
                'fecha_deteccion': date(2024, 10, 1), 'centro_trabajo': c2,
                'fecha_limite_resolucion': date(2024, 10, 15),
                'creado_por': admin,
            }
        )
        NoConformidad.objects.get_or_create(
            empresa=emp, codigo='NC-RS-002',
            defaults={
                'titulo': 'Trabajadores sin EPIs homologados', 'gravedad': 'grave',
                'estado': 'abierta', 'descripcion': '2 trabajadores usando cascos sin marca de conformidad',
                'fuente': 'interna', 'detectado_por': admin,
                'fecha_deteccion': date(2024, 11, 15), 'centro_trabajo': c2,
                'fecha_limite_resolucion': date(2024, 11, 30),
                'creado_por': admin,
            }
        )
        self.stdout.write('  No Conformidades: 2 ABIERTAS sin tratamiento (1 crítica)')

        # ── EPIs: BÁSICO ──
        from apps.epis.models import CatalogoEPI, EPI, EntregaEPI
        cat_casco, _ = CatalogoEPI.objects.get_or_create(
            nombre='Casco de seguridad', defaults={'categoria': 'cabeza', 'riesgos_proteccion': 'Impacto', 'norma_eu': 'EN 397'}
        )
        epi, _ = EPI.objects.get_or_create(
            empresa=emp, catalogo=cat_casco,
            defaults={'marca': 'Genérico', 'modelo': 'Básico', 'estado': 'asignado'}
        )
        EntregaEPI.objects.get_or_create(
            empresa=emp, epi=epi, trabajador=t[0], fecha_entrega=date(2024, 1, 15),
            defaults={'estado': 'activo', 'entregado_por': admin}
        )
        self.stdout.write('  EPIs: 1 catálogo, 1 asignado (4 trabajadores sin EPIs)')

        # ── Químicos: SIN FICHA ──
        from apps.chemical_products.models import ProductoQuimico
        ProductoQuimico.objects.get_or_create(
            company=emp, nombre='Cemento快dry',
            defaults={'fabricante': 'Desconocido', 'uso': 'Construcción', 'ubicacion': 'Obra'}
        )
        self.stdout.write('  Productos químicos: 1 SIN ficha de seguridad')

        # ── Vigilancia de la salud: MÍNIMA ──
        from apps.health_surveillance.models import ReconocimientoMedico
        ReconocimientoMedico.objects.get_or_create(
            company=emp, trabajador=t[0], fecha=date(2024, 2, 10),
            defaults={'tipo': 'inicial', 'apto': True, 'medico': 'Dr. Sevilla'}
        )
        self.stdout.write('  Vigilancia de la salud: 1 reconocimiento (4 sin reconocer)')

        # ── Equipos: SIN REVISAR ──
        from apps.work_equipment.models import TipoEquipo, EquipoTrabajo
        tipo_and, _ = TipoEquipo.objects.get_or_create(
            empresa=emp, nombre='Andamio modular',
            defaults={'categoria': 'andamios', 'descripcion': 'Andamio tubular modular'}
        )
        for i in range(2):
            EquipoTrabajo.objects.get_or_create(
                empresa=emp, tipo=tipo_and, nombre=f'Andamio-{i+1}',
                defaults={
                    'marca': 'Pere', 'modelo': 'Rapid',
                    'numero_serie': f'AND-RS-{i+1}', 'estado': 'operativo',
                    'ubicacion': 'Obra Viña Norte',
                    'notas': 'Sin revisiones registradas',
                }
            )
        self.stdout.write('  Equipos: 2 andamios SIN revisiones')

        # ── Auditorías: NINGUNA ──
        self.stdout.write('  Auditorías: NINGUNA')

        # ── Cumplimiento Legal: PARCIAL ──
        from apps.legal_requirements.models import CumplimientoLegal
        for req in self._requisitos_legales[:6]:
            CumplimientoLegal.objects.get_or_create(
                empresa=emp, requisito=req,
                defaults={
                    'estado': random.choice(['pendiente', 'no_cumple', 'pendiente', 'en_curso']),
                    'evaluado_por': admin, 'fecha_evaluacion': date(2024, random.randint(1, 6), 15),
                }
            )
        self.stdout.write(f'  Cumplimiento Legal: 6 requisitos (mayoría pendiente/no cumple)')

        # ── Instrucciones de trabajo: NINGUNA ──
        self.stdout.write('  Instrucciones de trabajo: NINGUNA')

        # ── CAE: NADA ──
        self.stdout.write('  CAE: NINGUNO')

        # ── Emergencia: NADA ──
        self.stdout.write('  Emergencias: NADA configurado')

        # ── Tareas pendientes ──
        from apps.tasks.models import Task
        Task.objects.get_or_create(
            company=emp, title='Actualizar evaluación de riesgos',
            defaults={
                'description': 'La evaluación está caducada desde 2022',
                'priority': 'critical', 'assigned_to': admin, 'created_by': admin,
                'due_date': date(2024, 12, 1), 'status': 'pending',
            }
        )
        Task.objects.get_or_create(
            company=emp, title='Formar a trabajadores sin formación PRL',
            defaults={
                'description': '3 trabajadores sin formación básica',
                'priority': 'high', 'assigned_to': admin, 'created_by': admin,
                'due_date': date(2025, 1, 15), 'status': 'pending',
            }
        )
        self.stdout.write('  Tareas: 2 pendientes (crítica y alta)')

        self.stdout.write(self.style.WARNING(f'  [!] Empresa C: deficiente - ~40% documentada\n'))

    # ══════════════════════════════════════════════════════════════════════
    #  EMPRESA D — TALLERES MECÁNICOS EL MOTOR S.A. (~10% documentada)
    # ══════════════════════════════════════════════════════════════════════
    def _crear_empresa_d(self, u):
        self.stdout.write(self.style.MIGRATE_HEADING(
            '\n-- EMPRESA D: Talleres Mecanicos El Motor S.A. (DESASTRE ~10%) --'
        ))
        emp = self._empresa(
            'A99999999', 'Talleres Mecánicos El Motor S.A.', 'El Motor',
            email='info@motor-test.com', phone='961234567',
            address='Polígono La Industria, Nave 3', postal_code='46010',
            city='Valencia', province='Valencia', ac='Comunidad Valenciana',
            activity='Reparación y mantenimiento de vehículos', cnae='4520', workforce=30,
        )
        admin = u['maria_motor']
        self._membresia(admin, emp, 'company_admin', True)
        self._membresia(u['admin_test'], emp, 'company_admin', False)

        # ── Centro de trabajo ──
        c1 = self._centro(emp, name='Taller Principal', code='TM-001',
                          address='Pol. La Industria, Nave 3', postal_code='46010',
                          city='Valencia', province='Valencia',
                          activity='Reparación mecánica', workers=30, risk='high')

        # ── Puestos ──
        p0 = self._puesto(emp, 'Mecánico', 'Taller')
        p1 = self._puesto(emp, 'Electricista automoción', 'Taller')
        p2 = self._puesto(emp, 'Recepcionista', 'Admin')

        # ── Trabajadores ──
        t = []
        for fn, ln, nif, centro, puesto in [
            ('Vicente', 'Ferrer Domínguez', '46111111A', c1, p0),
            ('Rosa', 'Navarro Campos', '46222222B', c1, p1),
            ('Javier', 'Pérez García', '46333333C', c1, p0),
            ('Elena', 'Soler Martínez', '46444444D', c1, p2),
        ]:
            t.append(self._trabajador(emp, fn, ln, nif, centro, puesto))
        self.stdout.write(f'  Centro: 1 | Puestos: 3 | Trabajadores: {len(t)}')

        # ── Plan de Prevención: MÍNIMO ──
        from apps.prevention_plan.models import PlanPrevention
        PlanPrevention.objects.get_or_create(
            company=emp,
            defaults={
                'politica_firmada': False,
                'delegado_prl': 'no',
                'recurso_preventivo': 'no',
            },
        )
        self.stdout.write('  Plan de Prevención: MÍNIMO (vacío)')

        # ── Evaluación de Riesgos: NADA ──
        self.stdout.write('  Evaluación de Riesgos: NINGUNA')

        # ── Formación: NADA ──
        self.stdout.write('  Formación: NINGUNA')

        # ── Documentos: NADA ──
        self.stdout.write('  Documentos: NINGUNO')

        # ── Inspecciones: NINGUNA ──
        self.stdout.write('  Inspecciones: NINGUNA')

        # ── Incidentes: MUCHOS SIN RESOLVER ──
        from apps.incidents.models import Incidente, Accidente
        titulos_inc = [
            'Caída de herramienta sobre pie de trabajador',
            'Chispas de soldadura sin protección',
            'Fuga de gasolina en zona de reparación',
            'Golpe contra foso de inspección',
            'Resbalón en zona de aceite derramado',
        ]
        for i, titulo in enumerate(titulos_inc):
            Incidente.objects.get_or_create(
                empresa=emp, codigo=f'INC-TM-{i+1:03d}',
                defaults={
                    'titulo': titulo,
                    'fecha': timezone.now() - timedelta(days=random.randint(5, 180)),
                    'centro_trabajo': c1,
                    'descripcion': 'Sin investigación. Sin medidas correctivas.',
                    'potencial_dano': random.choice(['moderada', 'grave', 'muy_grave']),
                    'gravedad_potencial': random.choice(['moderada', 'grave', 'muy_grave']),
                    'estado': 'abierto', 'creado_por': admin,
                }
            )

        Accidente.objects.get_or_create(
            empresa=emp, codigo='ACC-TM-001',
            defaults={
                'titulo': 'Quemadura con líquido de frenos caliente',
                'fecha': timezone.now() - timedelta(days=90),
                'centro_trabajo': c1, 'ubicacion': 'Foso de inspección',
                'tipo': 'trabajo', 'gravedad': 'baja_temporal',
                'tipo_lesion': 'quemaduras', 'parte_cuerpo': 'Antebrazo izquierdo',
                'descripcion': 'Trabajador derrama líquido de frenos caliente. No investigado.',
                'estado': 'abierto', 'creado_por': admin,
            }
        )
        Accidente.objects.get_or_create(
            empresa=emp, codigo='ACC-TM-002',
            defaults={
                'titulo': 'Atrapamiento en compresor de aire',
                'fecha': timezone.now() - timedelta(days=30),
                'centro_trabajo': c1, 'ubicacion': 'Zona de compresores',
                'tipo': 'trabajo', 'gravedad': 'baja_permanente',
                'tipo_lesion': 'atrapamiento', 'parte_cuerpo': 'Dedo índice mano derecha',
                'descripcion': 'Compresor sin protección. Trabajador sufre pérdida parcial de dedo.',
                'estado': 'abierto', 'creado_por': admin,
            }
        )
        self.stdout.write('  Incidentes/Accidentes: 2 accidentes (1 baja temporal, 1 permanente), 5 incidentes (TODOS ABIERTOS)')

        # ── No Conformidades: CRÍTICAS Y ABIERTAS ──
        from apps.corrective_actions.models import NoConformidad
        NoConformidad.objects.get_or_create(
            empresa=emp, codigo='NC-TM-001',
            defaults={
                'titulo': 'Foso de inspeccion sin proteccion perimetral',
                'gravedad': 'critica', 'estado': 'abierta',
                'descripcion': 'Foso de inspeccion sin barandillas ni proteccion perimetral. Riesgo de caida mortal.',
                'fuente': 'interna', 'detectado_por': admin,
                'fecha_deteccion': date(2024, 9, 1), 'centro_trabajo': c1,
                'fecha_limite_resolucion': date(2024, 9, 15),
                'creado_por': admin,
            }
        )
        NoConformidad.objects.get_or_create(
            empresa=emp, codigo='NC-TM-002',
            defaults={
                'titulo': 'Extintores caducados e inaccesibles',
                'gravedad': 'critica', 'estado': 'abierta',
                'descripcion': '4 extintores caducados, 2 bloqueados por herramientas. Imposible acceso en emergencia.',
                'fuente': 'inspeccion', 'detectado_por': admin,
                'fecha_deteccion': date(2024, 10, 15), 'centro_trabajo': c1,
                'fecha_limite_resolucion': date(2024, 10, 30),
                'creado_por': admin,
            }
        )
        NoConformidad.objects.get_or_create(
            empresa=emp, codigo='NC-TM-003',
            defaults={
                'titulo': 'Instalacion electrica con riesgo de electrocucion',
                'gravedad': 'critica', 'estado': 'abierta',
                'descripcion': 'Cables pelados, cuadro electrico sin tapa, conexiones provisionales. Riesgo de electrocucion.',
                'fuente': 'interna', 'detectado_por': admin,
                'fecha_deteccion': date(2024, 11, 20), 'centro_trabajo': c1,
                'fecha_limite_resolucion': date(2024, 11, 30),
                'creado_por': admin,
            }
        )
        self.stdout.write('  No Conformidades: 3 ABIERTAS CRÍTICAS sin ninguna acción')

        # ── EPIs: NADA ──
        self.stdout.write('  EPIs: NINGUNO')

        # ── Químicos: SIN NADA ──
        from apps.chemical_products.models import ProductoQuimico
        ProductoQuimico.objects.get_or_create(
            company=emp, nombre='Líquido de frenos DOT4',
            defaults={'fabricante': 'Genérico', 'uso': 'Sistemas de frenado', 'ubicacion': 'Zona de mecanica'}
        )
        ProductoQuimico.objects.get_or_create(
            company=emp, nombre='Aceite motor 10W40',
            defaults={'fabricante': 'Repsol', 'uso': 'Cambio de aceite', 'ubicacion': 'Almacén'}
        )
        self.stdout.write('  Productos químicos: 2 SIN fichas de seguridad')

        # ── Vigilancia de la salud: NADA ──
        self.stdout.write('  Vigilancia de la salud: NINGÚN reconocimiento')

        # ── Equipos: SIN REVISAR ──
        from apps.work_equipment.models import TipoEquipo, EquipoTrabajo
        tipo_h, _ = TipoEquipo.objects.get_or_create(
            empresa=emp, nombre='Gato hidráulico',
            defaults={'categoria': 'elevacion', 'descripcion': 'Gato hidráulico 3 toneladas'}
        )
        tipo_c, _ = TipoEquipo.objects.get_or_create(
            empresa=emp, nombre='Compresor de aire',
            defaults={'categoria': 'instalaciones', 'descripcion': 'Compresor tornillo industrial'}
        )
        for i in range(2):
            EquipoTrabajo.objects.get_or_create(
                empresa=emp, tipo=tipo_h, nombre=f'Gato-{i+1}',
                defaults={
                    'marca': 'Einhell', 'modelo': 'TH-EL 3000',
                    'numero_serie': f'GATO-{i+1}', 'estado': 'operativo',
                    'ubicacion': 'Taller', 'notas': 'Sin revisiones',
                }
            )
        EquipoTrabajo.objects.get_or_create(
            empresa=emp, tipo=tipo_c, nombre='Compresor Principal',
            defaults={
                'marca': 'Atlas Copco', 'modelo': 'GA 15',
                'numero_serie': 'COMP-001', 'estado': 'operativo',
                'ubicacion': 'Zona compresores', 'notas': 'Sin revisiones. Con NC abierta.',
            }
        )
        self.stdout.write('  Equipos: 3 SIN revisiones')

        # ── Auditorías: NADA ──
        self.stdout.write('  Auditorías: NINGUNA')

        # ── Cumplimiento Legal: TODO PENDIENTE ──
        from apps.legal_requirements.models import CumplimientoLegal
        for req in self._requisitos_legales[:6]:
            CumplimientoLegal.objects.get_or_create(
                empresa=emp, requisito=req,
                defaults={
                    'estado': random.choice(['pendiente', 'no_cumple', 'pendiente', 'no_cumple']),
                    'evaluado_por': admin, 'fecha_evaluacion': date(2024, random.randint(1, 6), 15),
                }
            )
        self.stdout.write(f'  Cumplimiento Legal: 6 requisitos (TODOS pendiente/no cumple)')

        # ── Instrucciones de trabajo: NADA ──
        self.stdout.write('  Instrucciones de trabajo: NINGUNA')

        # ── CAE: NADA ──
        self.stdout.write('  CAE: NINGUNO')

        # ── Emergencia: NADA ──
        self.stdout.write('  Emergencias: NADA')

        # ── Tareas acumuladas ──
        from apps.tasks.models import Task
        for titulo, prio in [
            ('URGENTE: Cerrar foso sin protección o paralizar zona', 'critical'),
            ('Reemplagar extintores caducados', 'critical'),
            ('Reparar instalación eléctrica', 'critical'),
            ('Realizar evaluación de riesgos', 'high'),
            ('Formar a todo el personal', 'high'),
        ]:
            Task.objects.get_or_create(
                company=emp, title=titulo,
                defaults={
                    'priority': prio, 'assigned_to': admin, 'created_by': admin,
                    'due_date': date(2025, 1, 1), 'status': 'pending',
                }
            )
        self.stdout.write('  Tareas: 5 pendientes (3 críticas, 2 altas)')

        self.stdout.write(self.style.ERROR(
            f'  [X] Empresa D: DESASTRE total - ~10% documentada\n'
            f'      RIESGOS CRÍTICOS DETECTADOS:\n'
            f'      - Foso sin protección (caída mortal)\n'
            f'      - Instalación eléctrica (electrocución)\n'
            f'      - Extintores caducados/bloqueados\n'
            f'      - Accidente con baja permanente SIN investigar\n'
            f'      - 5 incidentes SIN investigación\n'
            f'      - 0 formación, 0 EPIs, 0 evaluación de riesgos\n'
            f'      - 0 inspecciones, 0 auditorías, 0 vigilancia salud\n'
        ))

    # ══════════════════════════════════════════════════════════════════════
    #  RESUMEN FINAL
    # ══════════════════════════════════════════════════════════════════════
    def _resumen(self, u):
        from apps.companies.models import Company
        total_emp = Company.objects.count()
        total_users = User.objects.count()

        self.stdout.write(self.style.MIGRATE_HEADING('\n' + '=' * 60))
        self.stdout.write(self.style.MIGRATE_HEADING('  DATOS DE PRUEBA CARGADOS CORRECTAMENTE'))
        self.stdout.write(self.style.MIGRATE_HEADING('=' * 60))
        self.stdout.write(self.style.SUCCESS(
            f'\n  EMPRESAS: {total_emp}\n'
            f'  USUARIOS: {total_users}\n'
            f'  CONTRASEÑA PARA TODOS: test1234\n'
        ))
        self.stdout.write(self.style.SUCCESS('  USUARIOS Y ACCESOS:'))
        self.stdout.write('  +-----------------+------------------------------+------------------+')
        self.stdout.write('  | Usuario         | Empresa (por defecto)        | Rol              |')
        self.stdout.write('  +-----------------+------------------------------+------------------+')
        self.stdout.write('  | admin_test      | (todas - superuser)          | Superadmin       |')
        self.stdout.write('  | ana_alonso      | Alonso Industria (A)         | Admin empresa    |')
        self.stdout.write('  | pedro_tecnico   | Alonso Industria (A)         | Tecnico PRL      |')
        self.stdout.write('  | laura_norte     | Norte Logistica (B)          | Admin empresa    |')
        self.stdout.write('  | carlos_tecnico  | Norte Logistica (B)          | Tecnico PRL      |')
        self.stdout.write('  | jorge_rapida    | Rapida Sur (C)               | Admin empresa    |')
        self.stdout.write('  | maria_motor     | El Motor (D)                 | Admin empresa    |')
        self.stdout.write('  +-----------------+------------------------------+------------------+')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('  ESTADO DE LAS EMPRESAS:'))
        self.stdout.write('  +----+---------------------------------+----------+-------------------+')
        self.stdout.write('  |    | Empresa                         | Estado   | Documentacion     |')
        self.stdout.write('  +----+---------------------------------+----------+-------------------+')
        self.stdout.write('  | A  | Alonso Industria                | ACTIVA   | COMPLETA (100%)   |')
        self.stdout.write('  | B  | Norte Logistica                 | ACTIVA   | COMPLETA (100%)   |')
        self.stdout.write('  | C  | Rapida Sur (Construccion)       | ACTIVA   | DEFICIENTE (~40%) |')
        self.stdout.write('  | D  | El Motor (Talleres)             | ACTIVA   | DESASTRE (~10%)   |')
        self.stdout.write('  +----+---------------------------------+----------+-------------------+')
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('  MODULOS CUBIERTOS:'))
        self.stdout.write('  [x] Empresas, centros de trabajo, puestos, trabajadores')
        self.stdout.write('  [x] Plan de prevención (con documentos)')
        self.stdout.write('  [x] Evaluación de riesgos (INSST)')
        self.stdout.write('  [x] Formación y registros')
        self.stdout.write('  [x] Documentos con categorías')
        self.stdout.write('  [x] Inspecciones (plantillas + inspecciones)')
        self.stdout.write('  [x] Incidentes y accidentes')
        self.stdout.write('  [x] No conformidades + acciones correctivas')
        self.stdout.write('  [x] EPIs (catálogo, inventario, entregas, inspecciones)')
        self.stdout.write('  [x] Productos químicos + clasificación GHS')
        self.stdout.write('  [x] Vigilancia de la salud')
        self.stdout.write('  [x] Equipos de trabajo + revisiones')
        self.stdout.write('  [x] Auditorías ISO 45001 + checklist + informe')
        self.stdout.write('  [x] Cumplimiento legal y normativa')
        self.stdout.write('  [x] Instrucciones de trabajo')
        self.stdout.write('  [x] CAE (coordinación de actividades empresariales)')
        self.stdout.write('  [x] Medidas de emergencia (plan, equipos, simulacros)')
        self.stdout.write('  [x] Planificación preventiva')
        self.stdout.write('  [x] Enfermedades profesionales + investigación')
        self.stdout.write('  [x] Tareas y alertas')
        self.stdout.write('  [x] Niveles de riesgo INSST (referencia)')
        self.stdout.write('  [x] Marco legal (normativa + requisitos)')
        self.stdout.write('')
