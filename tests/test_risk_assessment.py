import pytest
from django.db import IntegrityError
from datetime import timedelta
from django.utils import timezone
from apps.risk_assessment.models import (
    TipoPeligro, EvaluacionRiesgos, ItemEvaluacionRiesgos,
    NivelRiesgoReferencia, InformeRiesgoEspecial,
)
from tests.factories import (
    CompanyFactory, TipoPeligroFactory, EvaluacionRiesgosFactory,
    ItemEvaluacionRiesgosFactory, NivelRiesgoReferenciaFactory,
    InformeRiesgoEspecialFactory, WorkCenterFactory, JobPositionFactory,
)


@pytest.mark.django_db
class TestTipoPeligro:
    def test_create_tipo_peligro(self):
        tp = TipoPeligroFactory(nombre='Ruido', codigo='RUI-001', categoria='fisico')
        assert tp.nombre == 'Ruido'
        assert tp.codigo == 'RUI-001'
        assert tp.categoria == 'fisico'
        assert tp.activo is True

    def test_codigo_unique(self):
        TipoPeligroFactory(codigo='UNQ-001')
        with pytest.raises(IntegrityError):
            TipoPeligroFactory(codigo='UNQ-001')

    def test_categoria_choices(self):
        for cat in ['mecanico', 'quimico', 'electrico', 'ergonomico', 'psicosocial',
                     'biologico', 'fisico', 'locativo', 'incendio', 'otro']:
            tp = TipoPeligroFactory(categoria=cat)
            assert tp.categoria == cat

    def test_str_representation(self):
        tp = TipoPeligroFactory(nombre='Vibraciones', categoria='mecanico')
        assert 'Vibraciones' in str(tp)
        assert 'Mecánico' in str(tp)


@pytest.mark.django_db
class TestEvaluacionRiesgos:
    def test_create_evaluacion(self):
        ev = EvaluacionRiesgosFactory(
            titulo='Evaluación Q1 2026',
            estado='borrador',
        )
        assert ev.titulo == 'Evaluación Q1 2026'
        assert ev.estado == 'borrador'
        assert ev.version == '1.0'

    def test_str_representation(self):
        ev = EvaluacionRiesgosFactory(titulo='Eval Test', estado='aprobada')
        assert 'Eval Test' in str(ev)

    def test_estado_choices(self):
        for estado in ['borrador', 'pendiente_aprobacion', 'aprobada', 'en_revision', 'expirada']:
            ev = EvaluacionRiesgosFactory(estado=estado)
            assert ev.estado == estado

    def test_total_items_property(self):
        ev = EvaluacionRiesgosFactory()
        jp = JobPositionFactory(company=ev.empresa)
        ItemEvaluacionRiesgosFactory(evaluacion=ev, puesto_trabajo=jp)
        ItemEvaluacionRiesgosFactory(evaluacion=ev, puesto_trabajo=jp)
        assert ev.total_items == 2

    def test_items_requieren_accion(self):
        ev = EvaluacionRiesgosFactory()
        jp = JobPositionFactory(company=ev.empresa)
        ItemEvaluacionRiesgosFactory(
            evaluacion=ev, puesto_trabajo=jp, probabilidad=3, severidad=3,
        )
        ItemEvaluacionRiesgosFactory(
            evaluacion=ev, puesto_trabajo=jp, probabilidad=1, severidad=1,
        )
        assert ev.items_requieren_accion == 1


@pytest.mark.django_db
class TestItemEvaluacionRiesgos:
    def test_create_item(self):
        item = ItemEvaluacionRiesgosFactory(
            factor_riesgo_condicion='Ruido en producción',
            probabilidad=2,
            severidad=3,
        )
        assert item.factor_riesgo_condicion == 'Ruido en producción'
        assert item.probabilidad == 2
        assert item.severidad == 3
        assert item.grado_riesgo == 6

    def test_grado_riesgo_calculation(self):
        for p, s, expected in [(1, 1, 1), (1, 2, 2), (2, 3, 6), (3, 3, 9)]:
            item = ItemEvaluacionRiesgosFactory(probabilidad=p, severidad=s)
            assert item.grado_riesgo == expected

    def test_nivel_riesgo_muy_bajo(self):
        item = ItemEvaluacionRiesgosFactory(probabilidad=1, severidad=1)
        assert item.grado_riesgo == 1
        assert item.nivel_riesgo == 'muy_bajo'

    def test_nivel_riesgo_bajo(self):
        item = ItemEvaluacionRiesgosFactory(probabilidad=1, severidad=3)
        assert item.grado_riesgo == 3
        assert item.nivel_riesgo == 'bajo'

    def test_nivel_riesgo_medio(self):
        item = ItemEvaluacionRiesgosFactory(probabilidad=2, severidad=3)
        assert item.grado_riesgo == 6
        assert item.nivel_riesgo == 'medio'

    def test_nivel_riesgo_alto(self):
        item = ItemEvaluacionRiesgosFactory(probabilidad=3, severidad=3)
        assert item.grado_riesgo == 9
        assert item.nivel_riesgo == 'muy_alto'

    def test_tipo_riesgo_choices(self):
        for tipo in ['evitable', 'monitorizable', 'no_evitable']:
            item = ItemEvaluacionRiesgosFactory(tipo_riesgo=tipo)
            assert item.tipo_riesgo == tipo

    def test_frecuencia_field(self):
        item = ItemEvaluacionRiesgosFactory(frecuencia='Mensual')
        assert item.frecuencia == 'Mensual'

    def test_requiere_accion_property(self):
        item_medio = ItemEvaluacionRiesgosFactory(probabilidad=2, severidad=3)
        assert item_medio.requiere_accion is True

        item_bajo = ItemEvaluacionRiesgosFactory(probabilidad=1, severidad=1)
        assert item_bajo.requiere_accion is False

    def test_riesgo_choices(self):
        riesgos = ['caidas_mismo_nivel', 'atrapamientos', 'golpes', 'cortes']
        for r in riesgos:
            item = ItemEvaluacionRiesgosFactory(riesgo=r)
            assert item.riesgo == r

    def test_str_representation(self):
        item = ItemEvaluacionRiesgosFactory(
            factor_riesgo_condicion='Ruido',
        )
        s = str(item)
        assert 'Ruido' in s
        assert 'GR=' in s


@pytest.mark.django_db
class TestInformeRiesgoEspecial:
    def test_create_informe(self):
        informe = InformeRiesgoEspecialFactory(
            tipo='higienico',
            titulo='Informe Higiénico Q1',
        )
        assert informe.tipo == 'higienico'
        assert informe.titulo == 'Informe Higiénico Q1'

    def test_tipo_choices(self):
        for tipo in ['higienico', 'psicosocial', 'ergonomico']:
            informe = InformeRiesgoEspecialFactory(tipo=tipo)
            assert informe.tipo == tipo

    def test_str_representation(self):
        informe = InformeRiesgoEspecialFactory(tipo='psicosocial', titulo='Psico Test')
        s = str(informe)
        assert 'Psicosocial' in s
        assert 'Psico Test' in s
