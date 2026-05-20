"""
Tests unitarios para RegistrarDevolucion.
Regla cubierta: RN8 — multa = 2.000 COP × días de retraso
"""
import uuid
import pytest
from datetime import date, timedelta

from app.application.use_cases.prestamos.registrar_devolucion import RegistrarDevolucion
from app.domain.entities.prestamo import Prestamo, EstadoPrestamo
from app.domain.entities.libro import Ejemplar, EstadoEjemplar
from app.domain.exceptions import PrestamoNoEncontrado, PrestamoYaDevuelto
from app.infrastructure.repositories.in_memory_prestamo_repository import InMemoryPrestamoRepository
from app.infrastructure.repositories.in_memory_libro_repository import InMemoryEjemplarRepository
from app.infrastructure.repositories.in_memory_multa_repository import InMemoryMultaRepository

HOY = date(2026, 5, 19)


def _make_prestamo(estudiante_id, ejemplar_id, dias_retraso=0, estado=EstadoPrestamo.ACTIVO):
    fecha_prestamo = HOY - timedelta(days=15 + dias_retraso)
    fecha_esperada = HOY - timedelta(days=dias_retraso)
    return Prestamo(
        id=str(uuid.uuid4()),
        estudiante_id=estudiante_id,
        ejemplar_id=ejemplar_id,
        fecha_prestamo=fecha_prestamo,
        fecha_devolucion_esperada=fecha_esperada,
        estado=estado,
    )


class TestRegistrarDevolucion:
    def setup_method(self):
        self.prestamo_repo = InMemoryPrestamoRepository()
        self.ejemplar_repo = InMemoryEjemplarRepository()
        self.multa_repo = InMemoryMultaRepository()
        self.uc = RegistrarDevolucion(self.prestamo_repo, self.ejemplar_repo, self.multa_repo)

    def test_devolucion_a_tiempo_no_genera_multa(self):
        """Devolución puntual → sin multa."""
        ej = Ejemplar(id="EJ-1", libro_id="LIB-1", estado=EstadoEjemplar.PRESTADO)
        self.ejemplar_repo.guardar(ej)
        p = _make_prestamo("EST-1", "EJ-1", dias_retraso=0)
        self.prestamo_repo.guardar(p)

        result = self.uc.execute(p.id, fecha_devolucion=HOY)

        assert result.dias_retraso == 0
        assert result.multa is None
        assert self.prestamo_repo.obtener_por_id(p.id).estado == EstadoPrestamo.DEVUELTO
        assert self.ejemplar_repo.obtener_por_id("EJ-1").estado == EstadoEjemplar.DISPONIBLE

    def test_devolucion_con_1_dia_retraso(self):
        """RN8: 1 día de retraso → multa de 2.000 COP."""
        ej = Ejemplar(id="EJ-2", libro_id="LIB-1", estado=EstadoEjemplar.PRESTADO)
        self.ejemplar_repo.guardar(ej)
        p = _make_prestamo("EST-1", "EJ-2", dias_retraso=1)
        self.prestamo_repo.guardar(p)

        result = self.uc.execute(p.id, fecha_devolucion=HOY)

        assert result.dias_retraso == 1
        assert result.multa is not None
        assert result.multa.monto == 2_000

    def test_devolucion_con_5_dias_retraso(self):
        """RN8: 5 días de retraso → multa de 10.000 COP."""
        ej = Ejemplar(id="EJ-3", libro_id="LIB-1", estado=EstadoEjemplar.PRESTADO)
        self.ejemplar_repo.guardar(ej)
        p = _make_prestamo("EST-1", "EJ-3", dias_retraso=5)
        self.prestamo_repo.guardar(p)

        result = self.uc.execute(p.id, fecha_devolucion=HOY)

        assert result.dias_retraso == 5
        assert result.multa.monto == 10_000

    def test_devolucion_con_15_dias_retraso(self):
        """RN8: 15 días de retraso → multa de 30.000 COP."""
        ej = Ejemplar(id="EJ-4", libro_id="LIB-1", estado=EstadoEjemplar.PRESTADO)
        self.ejemplar_repo.guardar(ej)
        p = _make_prestamo("EST-1", "EJ-4", dias_retraso=15)
        self.prestamo_repo.guardar(p)

        result = self.uc.execute(p.id, fecha_devolucion=HOY)

        assert result.multa.monto == 30_000

    def test_prestamo_inexistente_lanza_excepcion(self):
        with pytest.raises(PrestamoNoEncontrado):
            self.uc.execute("ID-FALSO", fecha_devolucion=HOY)

    def test_prestamo_ya_devuelto_lanza_excepcion(self):
        ej = Ejemplar(id="EJ-5", libro_id="LIB-1", estado=EstadoEjemplar.DISPONIBLE)
        self.ejemplar_repo.guardar(ej)
        p = _make_prestamo("EST-1", "EJ-5", estado=EstadoPrestamo.DEVUELTO)
        self.prestamo_repo.guardar(p)

        with pytest.raises(PrestamoYaDevuelto):
            self.uc.execute(p.id, fecha_devolucion=HOY)
