import pytest
from django.db import IntegrityError
from datetime import timedelta
from django.utils import timezone
from apps.corrective_actions.models import (
    NoConformidad, AccionCorrectiva, AccionPreventiva,
)
from tests.factories import (
    CompanyFactory, NoConformidadFactory, AccionCorrectivaFactory,
    AccionPreventivaFactory, UserFactory,
)


@pytest.mark.django_db
class TestNoConformidad:
    def test_create_nc(self):
        nc = NoConformidadFactory(
            titulo='Fallo en máquina',
            fuente='auditoria',
            gravedad='importante',
        )
        assert nc.titulo == 'Fallo en máquina'
        assert nc.fuente == 'auditoria'
        assert nc.gravedad == 'importante'
        assert nc.estado == 'abierta'

    def test_codigo_unique(self):
        NoConformidadFactory(codigo='NC-0001')
        with pytest.raises(IntegrityError):
            NoConformidadFactory(codigo='NC-0001')

    def test_str_representation(self):
        nc = NoConformidadFactory(codigo='NC-TEST', titulo='Test NC')
        assert str(nc) == 'NC-TEST - Test NC'

    def test_esta_vencida(self):
        nc = NoConformidadFactory(
            estado='abierta',
            fecha_limite_resolucion=timezone.localdate() - timedelta(days=5),
        )
        assert nc.esta_vencida is True

    def test_no_esta_vencida_futuro(self):
        nc = NoConformidadFactory(
            estado='abierta',
            fecha_limite_resolucion=timezone.localdate() + timedelta(days=30),
        )
        assert nc.esta_vencida is False

    def test_no_esta_vencida_cerrada(self):
        nc = NoConformidadFactory(
            estado='cerrada',
            fecha_limite_resolucion=timezone.localdate() - timedelta(days=5),
        )
        assert nc.esta_vencida is False

    def test_dias_restantes(self):
        nc = NoConformidadFactory(
            fecha_limite_resolucion=timezone.localdate() + timedelta(days=10),
        )
        assert nc.dias_restantes == 10

    def test_estado_choices(self):
        for estado in ['abierta', 'en_investigacion', 'en_tratamiento', 'resuelta', 'cerrada', 'cancelada']:
            nc = NoConformidadFactory(estado=estado)
            assert nc.estado == estado

    def test_gravedad_choices(self):
        for gravedad in ['menor', 'moderada', 'importante', 'critica']:
            nc = NoConformidadFactory(gravedad=gravedad)
            assert nc.gravedad == gravedad

    def test_badge_estado(self):
        nc = NoConformidadFactory(estado='abierta')
        assert nc.badge_estado == 'badge-danger'


@pytest.mark.django_db
class TestAccionCorrectiva:
    def test_create_ac(self):
        ac = AccionCorrectivaFactory(
            descripcion='Retreinar al personal',
            estado='pendiente',
        )
        assert ac.descripcion == 'Retreinar al personal'
        assert ac.estado == 'pendiente'

    def test_esta_vencida(self):
        ac = AccionCorrectivaFactory(
            estado='pendiente',
            fecha_limite=timezone.localdate() - timedelta(days=3),
        )
        assert ac.esta_vencida is True

    def test_no_esta_vencida_completada(self):
        ac = AccionCorrectivaFactory(
            estado='completada',
            fecha_limite=timezone.localdate() - timedelta(days=3),
        )
        assert ac.esta_vencida is False

    def test_estado_choices(self):
        for estado in ['pendiente', 'en_progreso', 'completada', 'cancelada']:
            ac = AccionCorrectivaFactory(estado=estado)
            assert ac.estado == estado


@pytest.mark.django_db
class TestAccionPreventiva:
    def test_create_ap(self):
        ap = AccionPreventivaFactory(
            titulo='Mejorar iluminación',
            descripcion='Instalar LEDs',
        )
        assert ap.titulo == 'Mejorar iluminación'
        assert ap.descripcion == 'Instalar LEDs'
        assert ap.estado == 'pendiente'

    def test_esta_vencida(self):
        ap = AccionPreventivaFactory(
            estado='pendiente',
            fecha_limite=timezone.localdate() - timedelta(days=7),
        )
        assert ap.esta_vencida is True

    def test_str_representation(self):
        ap = AccionPreventivaFactory(titulo='Acción Preventiva Test')
        assert str(ap) == 'Acción Preventiva Test'
