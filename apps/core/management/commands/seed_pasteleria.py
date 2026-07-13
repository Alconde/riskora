import io
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils import timezone
from datetime import timedelta
from apps.companies.models import Company, CompanyMembership
from apps.workcenters.models import WorkCenter
from apps.workers.models import Worker, JobPosition
from apps.accounts.models import User
from apps.training.models import TrainingCategory, TrainingCourse, TrainingRecord
from apps.documents.models import Document, DocumentCategory
from apps.tasks.models import Task, Alert
from apps.risk_assessment.models import EvaluacionRiesgos, ItemEvaluacionRiesgos
from apps.corrective_actions.models import NoConformidad
from apps.epis.models import CatalogoEPI, EPI
from apps.work_equipment.models import TipoEquipo, EquipoTrabajo
from apps.preventive_planning.models import ItemPlanificacion
from apps.prevention_plan.models import PlanPrevention
from apps.epps.models import EnfermedadProfesional


class Command(BaseCommand):
    help = 'Crea datos de ejemplo para Pasteleria Conde Melero (empresa 2)'

    def handle(self, *args, **options):
        today = timezone.localdate()
        c = Company.objects.get(pk=2)

        # --- User ---
        user, created = User.objects.get_or_create(
            username='pasteleria',
            defaults={
                'email': 'admin@condemelero.com',
                'first_name': 'Admin',
                'last_name': 'Conde Melero',
                'is_staff': False,
                'is_superuser': False,
            }
        )
        if created:
            user.set_password('Pasteleria2026!')
            user.save()
            self.stdout.write(self.style.SUCCESS('User: pasteleria / Pasteleria2026!'))

        CompanyMembership.objects.get_or_create(
            user=user, company=c,
            defaults={'role': 'company_admin', 'is_active': True, 'is_default': True}
        )

        # --- Work Centers ---
        wc_central, _ = WorkCenter.objects.get_or_create(
            company=c, name='Central Pasteleria',
            defaults={
                'address': 'Calle Horno 15', 'city': 'Madrid',
                'province': 'Madrid', 'postal_code': '28012',
            }
        )
        wc_taller, _ = WorkCenter.objects.get_or_create(
            company=c, name='Taller de Produccion',
            defaults={
                'address': 'Poligono Industrial Sur', 'city': 'Getafe',
                'province': 'Madrid', 'postal_code': '28906',
            }
        )
        self.stdout.write(self.style.SUCCESS('WorkCenters: 2'))

        # --- Job Positions ---
        jp_gerente, _ = JobPosition.objects.get_or_create(company=c, name='Gerente')
        jp_peluquero, _ = JobPosition.objects.get_or_create(company=c, name='Pastelero/a')
        jp_admin, _ = JobPosition.objects.get_or_create(company=c, name='Administrativo/a')
        self.stdout.write(self.style.SUCCESS('JobPositions: 3'))

        # --- Workers ---
        workers = []
        wd = [
            ('Maria', 'Lopez Garcia', '12345678A', jp_gerente, wc_central, '36500012A'),
            ('Carlos', 'Fernandez Ruiz', '23456789B', jp_peluquero, wc_central, '36500023B'),
            ('Ana', 'Martinez Sanchez', '34567890C', jp_peluquero, wc_taller, '36500034C'),
            ('Pedro', 'Sanchez Lopez', '45678901D', jp_admin, wc_central, '36500045D'),
            ('Laura', 'Garcia Perez', '56789012E', jp_peluquero, wc_taller, '36500056E'),
        ]
        for name, last, nif, jp, wc, ss in wd:
            w, _ = Worker.objects.get_or_create(
                company=c, first_name=name, last_name=last,
                defaults={
                    'national_id': nif, 'job_position': jp, 'work_center': wc,
                    'social_security_number': ss,
                    'email': f'{name.lower()}.{last.split()[0].lower()}@condemelero.com',
                    'phone': '612345678',
                    'hire_date': today - timedelta(days=365),
                }
            )
            workers.append(w)
        self.stdout.write(self.style.SUCCESS(f'Workers: {len(workers)}'))

        # --- Training ---
        tc_prevencion_cat, _ = TrainingCategory.objects.get_or_create(
            name='Seguridad', defaults={'code': 'SEG', 'is_active': True}
        )
        tc1, _ = TrainingCourse.objects.get_or_create(
            company=c, name='Prevencion de Riesgos Laborales',
            defaults={
                'category': tc_prevencion_cat, 'code': 'PRL-001',
                'description': 'Formacion basica PRL',
                'duration_hours': Decimal('40.00'),
                'requires_renewal': True, 'validity_value': 24, 'validity_unit': 'months',
            }
        )
        tc2, _ = TrainingCourse.objects.get_or_create(
            company=c, name='Uso de Extintores',
            defaults={
                'category': tc_prevencion_cat, 'code': 'EXT-001',
                'description': 'Manejo de extintores',
                'duration_hours': Decimal('8.00'),
                'requires_renewal': True, 'validity_value': 12, 'validity_unit': 'months',
            }
        )
        tc3, _ = TrainingCourse.objects.get_or_create(
            company=c, name='Primeros Auxilios',
            defaults={
                'category': tc_prevencion_cat, 'code': 'PA-001',
                'description': 'Primeros auxilios en el trabajo',
                'duration_hours': Decimal('16.00'),
                'requires_renewal': True, 'validity_value': 24, 'validity_unit': 'months',
            }
        )

        for w in workers[:3]:
            TrainingRecord.objects.get_or_create(
                company=c, worker=w, course=tc1,
                defaults={
                    'status': 'completed',
                    'completed_date': today - timedelta(days=180),
                    'expiry_date': today + timedelta(days=540),
                    'certificate_number': f'PRV-{w.id:04d}',
                    'created_by': user,
                }
            )
        TrainingRecord.objects.get_or_create(
            company=c, worker=workers[1], course=tc2,
            defaults={
                'status': 'completed',
                'completed_date': today - timedelta(days=90),
                'expiry_date': today + timedelta(days=275),
                'certificate_number': 'EXT-0002', 'created_by': user,
            }
        )
        TrainingRecord.objects.get_or_create(
            company=c, worker=workers[0], course=tc3,
            defaults={
                'status': 'completed',
                'completed_date': today - timedelta(days=60),
                'expiry_date': today + timedelta(days=305),
                'certificate_number': 'PA-0001', 'created_by': user,
            }
        )
        self.stdout.write(self.style.SUCCESS('Training records created'))

        # --- Documents ---
        dc, _ = DocumentCategory.objects.get_or_create(
            name='Planificacion', defaults={'slug': 'planificacion'}
        )
        dc2, _ = DocumentCategory.objects.get_or_create(
            name='Seguridad', defaults={'slug': 'seguridad'}
        )

        dummy_pdf = ContentFile(b'%PDF-1.4 dummy content', name='documento.pdf')

        doc1, created = Document.objects.get_or_create(
            company=c, title='Politica de Prevencion 2026',
            defaults={
                'category': dc, 'uploaded_by': user,
                'description': 'Politica de prevencion anual',
                'status': 'valid', 'expiry_date': today + timedelta(days=300),
                'file': dummy_pdf,
            }
        )
        doc2, created = Document.objects.get_or_create(
            company=c, title='Protocolo de limpieza',
            defaults={
                'category': dc2, 'uploaded_by': user,
                'description': 'Protocolo de limpieza del local',
                'status': 'valid', 'expiry_date': today + timedelta(days=180),
                'file': dummy_pdf,
            }
        )
        self.stdout.write(self.style.SUCCESS('Documents created'))

        # --- Tasks ---
        Task.objects.get_or_create(
            company=c, title='Revision extintores trimestral',
            defaults={
                'description': 'Revisar estado de todos los extintores del local',
                'priority': 'high', 'status': 'pending',
                'created_by': user, 'due_date': today + timedelta(days=15),
            }
        )
        Task.objects.get_or_create(
            company=c, title='Actualizar EPIs caducados',
            defaults={
                'description': 'Solicitar nuevos guantes y gafas de proteccion',
                'priority': 'medium', 'status': 'in_progress',
                'created_by': user, 'due_date': today + timedelta(days=30),
            }
        )
        self.stdout.write(self.style.SUCCESS('Tasks created'))

        # --- Risk Assessment ---
        eval1, _ = EvaluacionRiesgos.objects.get_or_create(
            empresa=c, centro_trabajo=wc_central,
            titulo='Evaluacion riesgos Pasteleria Central',
            defaults={
                'fecha_evaluacion': today - timedelta(days=60),
                'fecha_proxima_revision': today + timedelta(days=305),
                'metodologia': 'propio',
                'revisado_por': user,
                'estado': 'aprobada',
            }
        )
        ItemEvaluacionRiesgos.objects.get_or_create(
            evaluacion=eval1, puesto_trabajo=jp_peluquero,
            factor_riesgo_condicion='Quemaduras por contacto con superficies calientes',
            riesgo='quemaduras', defaults={
                'probabilidad': 2, 'severidad': 2, 'grado_riesgo': 4, 'nivel_riesgo': 'medio',
                'medidas_propuestas': 'Guantes termoresistentes, senales de aviso',
            }
        )
        ItemEvaluacionRiesgos.objects.get_or_create(
            evaluacion=eval1, puesto_trabajo=jp_peluquero,
            factor_riesgo_condicion='Resbalones en suelo mojado',
            riesgo='caidas_mismo_nivel', defaults={
                'probabilidad': 2, 'severidad': 1, 'grado_riesgo': 2, 'nivel_riesgo': 'bajo',
                'medidas_propuestas': 'Calzado antideslizante, limpieza inmediata',
            }
        )
        self.stdout.write(self.style.SUCCESS('Risk Assessment created'))

        # --- No Conformidad ---
        NoConformidad.objects.get_or_create(
            empresa=c, codigo='NC-2026-001',
            defaults={
                'titulo': 'Falta de rotulacion en zona de calderas',
                'descripcion': 'Se detecto la ausencia de senales de peligro en la zona de calderas.',
                'fuente': 'inspeccion', 'gravedad': 'moderada', 'estado': 'abierta',
                'detectado_por': user, 'fecha_deteccion': today - timedelta(days=10),
                'fecha_limite_resolucion': today + timedelta(days=20),
                'centro_trabajo': wc_taller,
            }
        )
        self.stdout.write(self.style.SUCCESS('No Conformidad created'))

        # --- EPIs ---
        cat1, _ = CatalogoEPI.objects.get_or_create(
            nombre='Guantes de proteccion termica',
            defaults={
                'categoria': 'manos',
                'riesgos_proteccion': 'Quemaduras por contacto con superficies calientes',
                'norma_eu': 'EN 407',
            }
        )
        cat2, _ = CatalogoEPI.objects.get_or_create(
            nombre='Calzado antideslizante',
            defaults={
                'categoria': 'pies',
                'riesgos_proteccion': 'Resbalones y caidas',
                'norma_eu': 'EN ISO 20345',
            }
        )
        EPI.objects.get_or_create(
            empresa=c, catalogo=cat1, marca='Moldex', modelo='G-500',
            defaults={'numero_serie': 'EPI-001', 'estado': 'asignado', 'vida_util_meses': 6}
        )
        EPI.objects.get_or_create(
            empresa=c, catalogo=cat2, marca='Cofra', modelo='Smart S1P',
            defaults={'numero_serie': 'EPI-002', 'estado': 'asignado', 'vida_util_meses': 24}
        )
        self.stdout.write(self.style.SUCCESS('EPIs created'))

        # --- Work Equipment ---
        te1, _ = TipoEquipo.objects.get_or_create(
            empresa=c, nombre='Batidora industrial',
            defaults={'categoria': 'maquinaria', 'descripcion': 'Batidora para grandes producciones'}
        )
        te2, _ = TipoEquipo.objects.get_or_create(
            empresa=c, nombre='Horno industrial',
            defaults={'categoria': 'instalaciones', 'descripcion': 'Horno de coccion profesional'}
        )
        EquipoTrabajo.objects.get_or_create(
            empresa=c, tipo=te1, nombre='Batidora Hobart 20L',
            defaults={
                'marca': 'Hobart', 'modelo': 'HLC-500',
                'numero_serie': 'EQ-001', 'estado': 'operativo',
                'fecha_compra': today - timedelta(days=730),
            }
        )
        EquipoTrabajo.objects.get_or_create(
            empresa=c, tipo=te2, nombre='Horno Rational iCombi',
            defaults={
                'marca': 'Rational', 'modelo': 'iCombi Pro 6-1/1',
                'numero_serie': 'EQ-002', 'estado': 'operativo',
                'fecha_compra': today - timedelta(days=365),
            }
        )
        self.stdout.write(self.style.SUCCESS('Work Equipment created'))

        # --- Planificacion Preventiva ---
        ItemPlanificacion.objects.get_or_create(
            empresa=c, factor_riesgo='Quemaduras por contacto con plancha',
            defaults={
                'ambito_puesto': 'Pastelero',
                'tipo_factor_riesgo': 'evitables',
                'riesgos': 'quemaduras',
                'medidas_preventivas': 'Guantes termoresistentes y formacion',
                'estado': 'implementada',
                'responsable': 'Maria Lopez Garcia',
                'fecha_objetivo': today - timedelta(days=30),
            }
        )
        ItemPlanificacion.objects.get_or_create(
            empresa=c, factor_riesgo='Ruido por maquinaria',
            defaults={
                'ambito_puesto': 'Pastelero',
                'tipo_factor_riesgo': 'monitorizables',
                'riesgos': 'sordera',
                'medidas_preventivas': ' Proteccion auditiva y medicion periodica',
                'estado': 'en_curso',
                'responsable': 'Carlos Fernandez Ruiz',
                'fecha_objetivo': today + timedelta(days=30),
            }
        )
        self.stdout.write(self.style.SUCCESS('Planificacion Preventiva created'))

        # --- Prevention Plan ---
        plan, _ = PlanPrevention.objects.get_or_create(company=c)
        plan.politica_firmada = True
        plan.politica_fecha_subida = today - timedelta(days=15)
        plan.delegado_prl = 'si'
        plan.delegado_fecha_designacion = today - timedelta(days=120)
        plan.delegado_formacion = True
        plan.recurso_preventivo = 'no_aplica'
        plan.utiliza_ett = False
        plan.tiene_teletrabajo = False
        plan.save()
        self.stdout.write(self.style.SUCCESS('Plan de Prevencion configured'))

        self.stdout.write(self.style.SUCCESS(
            '\n=== TODO CREADO ===\n'
            'Login: pasteleria / Pasteleria2026!\n'
            'Empresa: Pasteleria Conde Melero (ID=2)'
        ))
