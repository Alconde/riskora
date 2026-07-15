from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from apps.audit_log.services import AuditService


_audited_models = set()


def register_model(model_class):
    _audited_models.add(model_class)


def is_audited(model_class) -> bool:
    return model_class in _audited_models


@receiver(pre_save)
def capture_changes_before_save(sender, instance, **kwargs):
    if sender not in _audited_models:
        return

    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            changes = {}
            for field in sender._meta.fields:
                if field.name in ('updated_at', 'created_at'):
                    continue
                old_val = getattr(old_instance, field.name)
                new_val = getattr(instance, field.name)
                if old_val != new_val:
                    changes[field.name] = [str(old_val), str(new_val)]
            instance._audit_changes = changes
        except sender.DoesNotExist:
            instance._audit_changes = {}
    else:
        instance._audit_changes = {}


@receiver(post_save)
def audit_save_handler(sender, instance, created, **kwargs):
    if sender not in _audited_models:
        return
    action = 'create' if created else 'update'
    AuditService.log_crud(instance, action)


@receiver(post_delete)
def audit_delete_handler(sender, instance, **kwargs):
    if sender not in _audited_models:
        return
    AuditService.log_crud(instance, 'delete')


# ---------------------------------------------------------------------------
# Registro de modelos auditados
# Se registran todos los modelos del dominio que deben quedar registrados
# en el log de auditoría. Los modelos de infraestructura (AuditLog,
# RetentionPolicy) no se registran para evitar recursión.
# ---------------------------------------------------------------------------

def _register_all_models():
    from apps.companies.models import Company, CompanyMembership
    from apps.workcenters.models import WorkCenter
    from apps.workers.models import JobPosition, Worker
    from apps.documents.models import DocumentCategory, Document
    from apps.tasks.models import Task, Alert
    from apps.training.models import (
        TrainingCategory, TrainingCourse, TrainingRecord,
        TrainingDocument, TrainingRequirement, TrainingNeed, TrainingAlert,
    )
    from apps.risk_assessment.models import (
        TipoPeligro, EvaluacionRiesgos, ItemEvaluacionRiesgos,
        NivelRiesgoReferencia, InformeRiesgoEspecial,
    )
    from apps.corrective_actions.models import (
        NoConformidad, AccionCorrectiva, AccionPreventiva,
    )
    from apps.inspections.models import (
        PlantillaInspeccion, PlantillaInspeccionItem, Inspeccion, ItemInspeccion,
    )
    from apps.incidents.models import (
        CausaAccidente, Accidente, InvestigacionAccidente,
        ProcedimientoInvestigacion, Incidente,
    )
    from apps.epps.models import (
        EnfermedadProfesional, InvestigacionEEPP, ProcedimientoInvestigacionEEPP,
    )
    from apps.epis.models import (
        CatalogoEPI, EPI, EntregaEPI, InspeccionEPI,
        ProcedimientoEntrega, FirmaEntrega,
    )
    from apps.work_equipment.models import (
        TipoEquipo, EquipoTrabajo, RevisionEquipo, MantenimientoEquipo,
    )
    from apps.preventive_planning.models import (
        MedidaPreventivaCatalogo, ItemPlanificacion,
    )
    from apps.prevention_plan.models import PlanPrevention
    from apps.cae.models import (
        EmpresaSubcontrata, DocumentoCAETipo, DocumentoCAE,
        ProcedimientoCAE, CartaCAE, DocumentoRiesgosCAE,
    )
    from apps.emergency_measures.models import (
        MedioProteccionIncendios, EmpresaMedioProteccion, PlanAutoproteccion,
        EquipoEmergencia, MiembroEquipoEmergencia, RegistroSimulacro,
        EntregaInformacionEmergencia,
    )
    from apps.chemical_products.models import ProductoQuimico, ClasificacionQuimica
    from apps.health_surveillance.models import ReconocimientoMedico, ControlSalud
    from apps.work_instructions.models import InstruccionTrabajo
    from apps.audits.models import (
        ProgramaAuditoria, AuditoriaInterna, ChecklistAuditoria, InformeAuditoria,
    )
    from apps.legal_requirements.models import (
        NormativaLegal, RequisitoLegal, CumplimientoLegal, AlertaLegal,
    )
    from apps.authorizations.models import RequisitoAutorizacion, AutorizacionTrabajador

    models_to_audit = [
        Company, CompanyMembership,
        WorkCenter,
        JobPosition, Worker,
        DocumentCategory, Document,
        Task, Alert,
        TrainingCategory, TrainingCourse, TrainingRecord,
        TrainingDocument, TrainingRequirement, TrainingNeed, TrainingAlert,
        TipoPeligro, EvaluacionRiesgos, ItemEvaluacionRiesgos,
        NivelRiesgoReferencia, InformeRiesgoEspecial,
        NoConformidad, AccionCorrectiva, AccionPreventiva,
        PlantillaInspeccion, PlantillaInspeccionItem, Inspeccion, ItemInspeccion,
        CausaAccidente, Accidente, InvestigacionAccidente,
        ProcedimientoInvestigacion, Incidente,
        EnfermedadProfesional, InvestigacionEEPP, ProcedimientoInvestigacionEEPP,
        CatalogoEPI, EPI, EntregaEPI, InspeccionEPI,
        ProcedimientoEntrega, FirmaEntrega,
        TipoEquipo, EquipoTrabajo, RevisionEquipo, MantenimientoEquipo,
        MedidaPreventivaCatalogo, ItemPlanificacion,
        PlanPrevention,
        EmpresaSubcontrata, DocumentoCAETipo, DocumentoCAE,
        ProcedimientoCAE, CartaCAE, DocumentoRiesgosCAE,
        MedioProteccionIncendios, EmpresaMedioProteccion, PlanAutoproteccion,
        EquipoEmergencia, MiembroEquipoEmergencia, RegistroSimulacro,
        EntregaInformacionEmergencia,
        ProductoQuimico, ClasificacionQuimica,
        ReconocimientoMedico, ControlSalud,
        InstruccionTrabajo,
        ProgramaAuditoria, AuditoriaInterna, ChecklistAuditoria, InformeAuditoria,
        NormativaLegal, RequisitoLegal, CumplimientoLegal, AlertaLegal,
        RequisitoAutorizacion, AutorizacionTrabajador,
    ]

    for model in models_to_audit:
        register_model(model)


_register_all_models()
