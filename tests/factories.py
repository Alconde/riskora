import factory
from factory.django import DjangoModelFactory
from django.utils import timezone
from datetime import timedelta

from apps.accounts.models import User
from apps.companies.models import Company, CompanyMembership
from apps.workcenters.models import WorkCenter
from apps.workers.models import JobPosition, Worker
from apps.risk_assessment.models import (
    TipoPeligro, EvaluacionRiesgos, ItemEvaluacionRiesgos,
    NivelRiesgoReferencia, InformeRiesgoEspecial,
)
from apps.corrective_actions.models import (
    NoConformidad, AccionCorrectiva, AccionPreventiva,
)
from apps.incidents.models import (
    CausaAccidente, Accidente, InvestigacionAccidente, Incidente,
)
from apps.training.models import (
    TrainingCategory, TrainingCourse, TrainingRecord,
)
from apps.documents.models import DocumentCategory, Document
from apps.tasks.models import Task, Alert
from apps.epis.models import CatalogoEPI, EPI, EntregaEPI, InspeccionEPI
from apps.work_equipment.models import TipoEquipo, EquipoTrabajo, RevisionEquipo


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@test.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    role = User.Role.TECHNICIAN
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')


class SuperUserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'super{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@test.com')
    is_superuser = True
    is_staff = True
    password = factory.PostGenerationMethodCall('set_password', 'adminpass123')


class CompanyFactory(DjangoModelFactory):
    class Meta:
        model = Company

    legal_name = factory.Sequence(lambda n: f'Empresa {n} S.L.')
    trade_name = factory.LazyAttribute(lambda o: o.legal_name)
    tax_id = factory.Sequence(lambda n: f'B{12345678 + n}')
    email = factory.LazyAttribute(lambda o: f'info@{o.trade_name.lower().replace(" ", "")}.com')
    phone = '912345678'
    city = 'Madrid'
    province = 'Madrid'
    workforce_size = 50


class CompanyMembershipFactory(DjangoModelFactory):
    class Meta:
        model = CompanyMembership

    user = factory.SubFactory(UserFactory)
    company = factory.SubFactory(CompanyFactory)
    role = CompanyMembership.Role.READER
    is_active = True
    is_default = False


class WorkCenterFactory(DjangoModelFactory):
    class Meta:
        model = WorkCenter

    company = factory.SubFactory(CompanyFactory)
    name = factory.Sequence(lambda n: f'Centro {n}')
    code = factory.Sequence(lambda n: f'C-{n:03d}')
    city = 'Madrid'
    worker_count = 10
    risk_level = 'medium'


class JobPositionFactory(DjangoModelFactory):
    class Meta:
        model = JobPosition

    company = factory.SubFactory(CompanyFactory)
    name = factory.Sequence(lambda n: f'Puesto {n}')
    department = 'Producción'


class WorkerFactory(DjangoModelFactory):
    class Meta:
        model = Worker

    company = factory.SubFactory(CompanyFactory)
    work_center = factory.SubFactory(WorkCenterFactory)
    job_position = factory.SubFactory(JobPositionFactory)
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    national_id = factory.Sequence(lambda n: f'12345678{n % 10}A')
    employee_code = factory.Sequence(lambda n: f'EMP-{n:04d}')


class TipoPeligroFactory(DjangoModelFactory):
    class Meta:
        model = TipoPeligro

    nombre = factory.Sequence(lambda n: f'Peligro {n}')
    codigo = factory.Sequence(lambda n: f'TP-{n:03d}')
    categoria = 'mecanico'


class EvaluacionRiesgosFactory(DjangoModelFactory):
    class Meta:
        model = EvaluacionRiesgos

    empresa = factory.SubFactory(CompanyFactory)
    centro_trabajo = factory.SubFactory(WorkCenterFactory)
    titulo = factory.Sequence(lambda n: f'Evaluación {n}')
    fecha_evaluacion = factory.LazyFunction(timezone.localdate)
    fecha_proxima_revision = factory.LazyFunction(
        lambda: timezone.localdate() + timedelta(days=365)
    )
    revisado_por = factory.SubFactory(UserFactory)
    estado = 'borrador'


class ItemEvaluacionRiesgosFactory(DjangoModelFactory):
    class Meta:
        model = ItemEvaluacionRiesgos

    evaluacion = factory.SubFactory(EvaluacionRiesgosFactory)
    puesto_trabajo = factory.SubFactory(JobPositionFactory)
    tipo_riesgo = 'evitable'
    factor_riesgo_condicion = factory.Faker('sentence', nb_words=4)
    probabilidad = 2
    severidad = 2


class NivelRiesgoReferenciaFactory(DjangoModelFactory):
    class Meta:
        model = NivelRiesgoReferencia

    grado = factory.Sequence(lambda n: n + 1)
    probabilidad = 1
    severidad = 1
    nivel = 'bajo'
    etiqueta = 'Bajo'


class InformeRiesgoEspecialFactory(DjangoModelFactory):
    class Meta:
        model = InformeRiesgoEspecial

    company = factory.SubFactory(CompanyFactory)
    tipo = 'higienico'
    titulo = factory.Sequence(lambda n: f'Informe {n}')
    fecha = factory.LazyFunction(timezone.localdate)


class NoConformidadFactory(DjangoModelFactory):
    class Meta:
        model = NoConformidad

    empresa = factory.SubFactory(CompanyFactory)
    codigo = factory.Sequence(lambda n: f'NC-{n:04d}')
    titulo = factory.Sequence(lambda n: f'No conformidad {n}')
    descripcion = factory.Faker('paragraph')
    fuente = 'interna'
    gravedad = 'moderada'
    estado = 'abierta'
    fecha_deteccion = factory.LazyFunction(timezone.localdate)
    fecha_limite_resolucion = factory.LazyFunction(
        lambda: timezone.localdate() + timedelta(days=30)
    )


class AccionCorrectivaFactory(DjangoModelFactory):
    class Meta:
        model = AccionCorrectiva

    no_conformidad = factory.SubFactory(NoConformidadFactory)
    descripcion = factory.Faker('paragraph')
    fecha_limite = factory.LazyFunction(
        lambda: timezone.localdate() + timedelta(days=15)
    )
    estado = 'pendiente'


class AccionPreventivaFactory(DjangoModelFactory):
    class Meta:
        model = AccionPreventiva

    empresa = factory.SubFactory(CompanyFactory)
    titulo = factory.Sequence(lambda n: f'Acción preventiva {n}')
    descripcion = factory.Faker('paragraph')
    fecha_limite = factory.LazyFunction(
        lambda: timezone.localdate() + timedelta(days=30)
    )
    estado = 'pendiente'


class CausaAccidenteFactory(DjangoModelFactory):
    class Meta:
        model = CausaAccidente

    empresa = factory.SubFactory(CompanyFactory)
    nombre = factory.Sequence(lambda n: f'Causa {n}')
    categoria = 'inmediata'


class AccidenteFactory(DjangoModelFactory):
    class Meta:
        model = Accidente

    empresa = factory.SubFactory(CompanyFactory)
    codigo = factory.Sequence(lambda n: f'ACC-{n:04d}')
    titulo = factory.Sequence(lambda n: f'Accidente {n}')
    fecha = factory.LazyFunction(timezone.now)
    centro_trabajo = factory.SubFactory(WorkCenterFactory)
    tipo = 'trabajo'
    gravedad = 'sin_baja'
    tipo_lesion = 'otro'
    descripcion = factory.Faker('paragraph')
    estado = 'abierto'


class InvestigacionAccidenteFactory(DjangoModelFactory):
    class Meta:
        model = InvestigacionAccidente

    accidente = factory.SubFactory(AccidenteFactory)
    fecha_inicio = factory.LazyFunction(timezone.localdate)
    metodologia = '_5_porques'
    estado = 'en_curso'


class IncidenteFactory(DjangoModelFactory):
    class Meta:
        model = Incidente

    empresa = factory.SubFactory(CompanyFactory)
    codigo = factory.Sequence(lambda n: f'INC-{n:04d}')
    titulo = factory.Sequence(lambda n: f'Incidente {n}')
    fecha = factory.LazyFunction(timezone.now)
    centro_trabajo = factory.SubFactory(WorkCenterFactory)
    descripcion = factory.Faker('paragraph')
    gravedad_potencial = 'leve'
    estado = 'abierto'


class TrainingCategoryFactory(DjangoModelFactory):
    class Meta:
        model = TrainingCategory

    name = factory.Sequence(lambda n: f'Categoría {n}')
    code = factory.Sequence(lambda n: f'CAT-{n:03d}')
    is_active = True


class TrainingCourseFactory(DjangoModelFactory):
    class Meta:
        model = TrainingCourse

    company = factory.SubFactory(CompanyFactory)
    category = factory.SubFactory(TrainingCategoryFactory)
    name = factory.Sequence(lambda n: f'Curso {n}')
    code = factory.Sequence(lambda n: f'CRS-{n:03d}')
    modality = 'presential'
    duration_hours = 8
    is_mandatory = True
    requires_renewal = False
    status = 'active'


class TrainingRecordFactory(DjangoModelFactory):
    class Meta:
        model = TrainingRecord

    company = factory.SubFactory(CompanyFactory)
    worker = factory.SubFactory(WorkerFactory)
    course = factory.SubFactory(TrainingCourseFactory)
    status = 'planned'
    planned_date = factory.LazyFunction(timezone.localdate)


class DocumentCategoryFactory(DjangoModelFactory):
    class Meta:
        model = DocumentCategory

    name = factory.Sequence(lambda n: f'Categoría doc {n}')
    slug = factory.Sequence(lambda n: f'cat-doc-{n}')
    scope = 'general'


class DocumentFactory(DjangoModelFactory):
    class Meta:
        model = Document

    company = factory.SubFactory(CompanyFactory)
    category = factory.SubFactory(DocumentCategoryFactory)
    title = factory.Sequence(lambda n: f'Documento {n}')
    version = '1.0'
    status = 'valid'


class TaskFactory(DjangoModelFactory):
    class Meta:
        model = Task

    company = factory.SubFactory(CompanyFactory)
    title = factory.Sequence(lambda n: f'Tarea {n}')
    description = factory.Faker('paragraph')
    status = 'pending'
    priority = 'medium'


class AlertFactory(DjangoModelFactory):
    class Meta:
        model = Alert

    company = factory.SubFactory(CompanyFactory)
    title = factory.Sequence(lambda n: f'Alerta {n}')
    message = factory.Faker('paragraph')
    alert_type = 'generic'
    severity = 'warning'


class CatalogoEPIFactory(DjangoModelFactory):
    class Meta:
        model = CatalogoEPI

    nombre = factory.Sequence(lambda n: f'EPI Catálogo {n}')
    categoria = 'cabeza'
    riesgos_proteccion = 'Impactos'
    norma_eu = 'EN 397'


class EPIFactory(DjangoModelFactory):
    class Meta:
        model = EPI

    empresa = factory.SubFactory(CompanyFactory)
    catalogo = factory.SubFactory(CatalogoEPIFactory)
    marca = '3M'
    modelo = factory.Sequence(lambda n: f'Modelo {n}')
    numero_serie = factory.Sequence(lambda n: f'SN-{n:06d}')
    estado = 'disponible'


class EntregaEPIFactory(DjangoModelFactory):
    class Meta:
        model = EntregaEPI

    empresa = factory.SubFactory(CompanyFactory)
    epi = factory.SubFactory(EPIFactory)
    trabajador = factory.SubFactory(WorkerFactory)
    fecha_entrega = factory.LazyFunction(timezone.localdate)
    estado = 'activo'


class InspeccionEPIFactory(DjangoModelFactory):
    class Meta:
        model = InspeccionEPI

    empresa = factory.SubFactory(CompanyFactory)
    epi = factory.SubFactory(EPIFactory)
    fecha = factory.LazyFunction(timezone.localdate)
    resultado = 'bueno'


class TipoEquipoFactory(DjangoModelFactory):
    class Meta:
        model = TipoEquipo

    empresa = factory.SubFactory(CompanyFactory)
    nombre = factory.Sequence(lambda n: f'Tipo equipo {n}')
    categoria = 'herramientas'


class EquipoTrabajoFactory(DjangoModelFactory):
    class Meta:
        model = EquipoTrabajo

    empresa = factory.SubFactory(CompanyFactory)
    tipo = factory.SubFactory(TipoEquipoFactory)
    nombre = factory.Sequence(lambda n: f'Equipo {n}')
    marca = 'DeWalt'
    modelo = factory.Sequence(lambda n: f'Modelo-E-{n}')
    numero_serie = factory.Sequence(lambda n: f'EQ-{n:06d}')
    estado = 'operativo'


class RevisionEquipoFactory(DjangoModelFactory):
    class Meta:
        model = RevisionEquipo

    empresa = factory.SubFactory(CompanyFactory)
    equipo = factory.SubFactory(EquipoTrabajoFactory)
    fecha = factory.LazyFunction(timezone.localdate)
    resultado = 'conforme'
    proxima_revision = factory.LazyFunction(
        lambda: timezone.localdate() + timedelta(days=180)
    )
