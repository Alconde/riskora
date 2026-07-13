import pytest
from django.db import IntegrityError
from apps.work_equipment.models import TipoEquipo, EquipoTrabajo, RevisionEquipo
from tests.factories import (
    CompanyFactory, TipoEquipoFactory, EquipoTrabajoFactory, RevisionEquipoFactory,
    UserFactory,
)


@pytest.mark.django_db
class TestTipoEquipo:
    def test_create_tipo(self):
        tipo = TipoEquipoFactory(nombre='Taladro', categoria='herramientas')
        assert tipo.nombre == 'Taladro'
        assert tipo.categoria == 'herramientas'
        assert tipo.activo is True

    def test_categoria_choices(self):
        for cat in ['maquinaria', 'herramientas', 'vehiculos', 'andamios',
                     'gruas', 'escaleras', 'elevacion', 'instalaciones', 'otro']:
            tipo = TipoEquipoFactory(categoria=cat)
            assert tipo.categoria == cat

    def test_str_representation(self):
        tipo = TipoEquipoFactory(nombre='Sierra')
        assert 'Sierra' in str(tipo)


@pytest.mark.django_db
class TestEquipoTrabajo:
    def test_create_equipo(self):
        eq = EquipoTrabajoFactory(
            nombre='Taladro Industrial',
            marca='Bosch',
            modelo='GBH 2-26',
            numero_serie='BS-001',
            estado='operativo',
        )
        assert eq.nombre == 'Taladro Industrial'
        assert eq.marca == 'Bosch'
        assert eq.estado == 'operativo'

    def test_estado_choices(self):
        for estado in ['operativo', 'en_mantenimiento', 'retirado', 'baja']:
            eq = EquipoTrabajoFactory(estado=estado)
            assert eq.estado == estado

    def test_str_representation(self):
        eq = EquipoTrabajoFactory(nombre='Compresor')
        assert 'Compresor' in str(eq)

    def test_document_fields_optional(self):
        eq = EquipoTrabajoFactory()
        assert eq.manual_instrucciones is None or eq.manual_instrucciones == ''
        assert eq.declaracion_ce is None or eq.declaracion_ce == ''
        assert eq.certificado_instalacion is None or eq.certificado_instalacion == ''


@pytest.mark.django_db
class TestRevisionEquipo:
    def test_create_revision(self):
        user = UserFactory()
        rev = RevisionEquipoFactory(
            resultado='conforme',
            realizado_por=user,
        )
        assert rev.resultado == 'conforme'
        assert rev.realizado_por == user

    def test_resultado_choices(self):
        for res in ['conforme', 'observaciones', 'no_conforme', 'reparado']:
            rev = RevisionEquipoFactory(resultado=res)
            assert rev.resultado == res

    def test_cascade_delete_equipo(self):
        eq = EquipoTrabajoFactory()
        RevisionEquipoFactory(equipo=eq)
        RevisionEquipoFactory(equipo=eq)
        eq.delete()
        assert RevisionEquipo.objects.count() == 0
