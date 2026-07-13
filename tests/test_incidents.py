import pytest
from django.db import IntegrityError
from apps.incidents.models import (
    CausaAccidente, Accidente, InvestigacionAccidente, Incidente,
)
from tests.factories import (
    CompanyFactory, CausaAccidenteFactory, AccidenteFactory,
    InvestigacionAccidenteFactory, IncidenteFactory, WorkCenterFactory,
)


@pytest.mark.django_db
class TestCausaAccidente:
    def test_create_causa(self):
        causa = CausaAccidenteFactory(nombre='Falta de EPI', categoria='inmediata')
        assert causa.nombre == 'Falta de EPI'
        assert causa.categoria == 'inmediata'
        assert causa.activa is True

    def test_categoria_choices(self):
        for cat in ['inmediata', 'basica', 'organizativa']:
            causa = CausaAccidenteFactory(categoria=cat)
            assert causa.categoria == cat

    def test_str_representation(self):
        causa = CausaAccidenteFactory(nombre='Fallo máquina')
        assert str(causa) == 'Fallo máquina'


@pytest.mark.django_db
class TestAccidente:
    def test_create_accidente(self):
        acc = AccidenteFactory(
            titulo='Caída en almacén',
            tipo='trabajo',
            gravedad='baja_temporal',
            tipo_lesion='caida',
        )
        assert acc.titulo == 'Caída en almacén'
        assert acc.tipo == 'trabajo'
        assert acc.gravedad == 'baja_temporal'
        assert acc.tipo_lesion == 'caida'
        assert acc.estado == 'abierto'

    def test_codigo_unique(self):
        AccidenteFactory(codigo='ACC-0001')
        with pytest.raises(IntegrityError):
            AccidenteFactory(codigo='ACC-0001')

    def test_str_representation(self):
        acc = AccidenteFactory(codigo='ACC-TEST', titulo='Test Accidente')
        assert str(acc) == 'ACC-TEST - Test Accidente'

    def test_estado_choices(self):
        for estado in ['abierto', 'en_investigacion', 'cerrado']:
            acc = AccidenteFactory(estado=estado)
            assert acc.estado == estado

    def test_gravedad_choices(self):
        for gravedad in ['sin_baja', 'baja_temporal', 'baja_permanente', 'mortal']:
            acc = AccidenteFactory(gravedad=gravedad)
            assert acc.gravedad == gravedad

    def test_tiene_investigacion(self):
        acc = AccidenteFactory()
        InvestigacionAccidenteFactory(accidente=acc)
        assert acc.tiene_investigacion is True

    def test_no_tiene_investigacion(self):
        acc = AccidenteFactory()
        assert acc.tiene_investigacion is False

    def test_badge_estado(self):
        acc = AccidenteFactory(estado='abierto')
        assert acc.badge_estado == 'badge-danger'


@pytest.mark.django_db
class TestInvestigacionAccidente:
    def test_create_investigacion(self):
        inv = InvestigacionAccidenteFactory(
            metodologia='ishikawa',
            estado='en_curso',
        )
        assert inv.metodologia == 'ishikawa'
        assert inv.estado == 'en_curso'

    def test_one_to_one_accidente(self):
        acc = AccidenteFactory()
        inv = InvestigacionAccidenteFactory(accidente=acc)
        assert inv.accidente == acc
        assert acc.investigacion == inv

    def test_str_representation(self):
        acc = AccidenteFactory(codigo='ACC-INV')
        inv = InvestigacionAccidenteFactory(accidente=acc)
        assert 'ACC-INV' in str(inv)

    def test_estado_choices(self):
        for estado in ['en_curso', 'completada']:
            inv = InvestigacionAccidenteFactory(estado=estado)
            assert inv.estado == estado


@pytest.mark.django_db
class TestIncidente:
    def test_create_incidente(self):
        inc = IncidenteFactory(
            titulo='Casi caída',
            gravedad_potencial='moderada',
        )
        assert inc.titulo == 'Casi caída'
        assert inc.gravedad_potencial == 'moderada'
        assert inc.estado == 'abierto'

    def test_codigo_unique(self):
        IncidenteFactory(codigo='INC-0001')
        with pytest.raises(IntegrityError):
            IncidenteFactory(codigo='INC-0001')

    def test_str_representation(self):
        inc = IncidenteFactory(codigo='INC-TEST', titulo='Test Incidente')
        assert str(inc) == 'INC-TEST - Test Incidente'

    def test_gravedad_potencial_choices(self):
        for gp in ['leve', 'moderada', 'grave', 'muy_grave']:
            inc = IncidenteFactory(gravedad_potencial=gp)
            assert inc.gravedad_potencial == gp
