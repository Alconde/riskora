import pytest
from django.db import IntegrityError
from apps.epis.models import CatalogoEPI, EPI, EntregaEPI, InspeccionEPI
from tests.factories import (
    CompanyFactory, CatalogoEPIFactory, EPIFactory, EntregaEPIFactory,
    InspeccionEPIFactory, WorkerFactory,
)


@pytest.mark.django_db
class TestCatalogoEPI:
    def test_create_catalogo(self):
        cat = CatalogoEPIFactory(
            nombre='Casco de seguridad',
            categoria='cabeza',
            norma_eu='EN 397',
        )
        assert cat.nombre == 'Casco de seguridad'
        assert cat.categoria == 'cabeza'
        assert cat.norma_eu == 'EN 397'
        assert cat.activo is True

    def test_categoria_choices(self):
        for cat in ['cabeza', 'manos', 'pies', 'oidos', 'respiratoria', 'corporal', 'otro']:
            c = CatalogoEPIFactory(categoria=cat)
            assert c.categoria == cat

    def test_str_representation(self):
        cat = CatalogoEPIFactory(nombre='Guantes')
        assert 'Guantes' in str(cat)


@pytest.mark.django_db
class TestEPI:
    def test_create_epi(self):
        epi = EPIFactory(
            marca='3M',
            modelo='X-100',
            numero_serie='SN-001',
            estado='disponible',
        )
        assert epi.marca == '3M'
        assert epi.modelo == 'X-100'
        assert epi.estado == 'disponible'

    def test_estado_choices(self):
        for estado in ['disponible', 'asignado', 'en_mantenimiento', 'retirado']:
            epi = EPIFactory(estado=estado)
            assert epi.estado == estado

    def test_str_representation(self):
        epi = EPIFactory(marca='MSA', modelo='HardHat')
        s = str(epi)
        assert 'MSA' in s or 'HardHat' in s


@pytest.mark.django_db
class TestEntregaEPI:
    def test_create_entrega(self):
        worker = WorkerFactory()
        epi = EPIFactory(estado='disponible')
        entrega = EntregaEPIFactory(
            epi=epi,
            trabajador=worker,
            estado='activo',
        )
        assert entrega.epi == epi
        assert entrega.trabajador == worker
        assert entrega.estado == 'activo'

    def test_estado_choices(self):
        for estado in ['activo', 'devuelto', 'caducado', 'reemplazado']:
            epi = EPIFactory()
            entrega = EntregaEPIFactory(epi=epi, estado=estado)
            assert entrega.estado == estado


@pytest.mark.django_db
class TestInspeccionEPI:
    def test_create_inspeccion(self):
        insp = InspeccionEPIFactory(
            resultado='bueno',
            observaciones='Sin novedad',
        )
        assert insp.resultado == 'bueno'
        assert insp.observaciones == 'Sin novedad'

    def test_resultado_choices(self):
        for res in ['bueno', 'regular', 'malo', 'rechazado']:
            insp = InspeccionEPIFactory(resultado=res)
            assert insp.resultado == res
