"""
Tests unitarios para RenovarPrestamo.
Regla cubierta: RN7 renovacion bloqueada si hay lista de espera
"""
import uuid
import pytest
from datetime import date, timedelta

from app.application.use_cases.prestamos.renovar_prestamo import RenovarPrestamo
from app.domain.entities.libro import Libro, Ejemplar, EstadoEjemplar
from app.domain.entities.prestamo import Prestamo, EstadoPrestamo
from app.domain.entities.reserva import Reserva, EstadoReserva
from app.domain.exceptions import RenovacionBloqueadaPorReserva, PrestamoNoEncontrado
from app.infrastructure.repositories.in_memory_prestamo_repository import InMemoryPrestamoRepository
from app.infrastructure.repositories.in_memory_libro_repository import (
    InMemoryLibroRepository, InMemoryEjemplarRepository
)
from app.infrastructure.repositories.in_memory_reserva_repository import InMemoryReservaRepository

HOY = date(2026, 5, 19)


class TestRenovarPrestamo:
    def setup_method(self):
        self.prestamo_repo = InMemoryPrestamoRepository()
        self.ejemplar_repo = InMemoryEjemplarRepository()
        self.libro_repo = InMemoryLibroRepository()
        self.reserva_repo = InMemoryReservaRepository()
        self.uc = RenovarPrestamo(
            self.prestamo_repo, self.ejemplar_repo,
            self.libro_repo, self.reserva_repo
        )
        self.libro = Libro(id="LIB-001", titulo="Clean Code", autor="Martin",
                           sala="General", alta_demanda=False)
        self.libro_repo.guardar(self.libro)
        self.ej = Ejemplar(id="EJ-001", libro_id="LIB-001",
                           estado=EstadoEjemplar.PRESTADO)
        self.ejemplar_repo.guardar(self.ej)
        self.prestamo = Prestamo(
            id=str(uuid.uuid4()),
            estudiante_id="EST-001",
            ejemplar_id="EJ-001",
            fecha_prestamo=HOY - timedelta(days=10),
            fecha_devolucion_esperada=HOY + timedelta(days=5),
            estado=EstadoPrestamo.ACTIVO,
        )
        self.prestamo_repo.guardar(self.prestamo)

    def test_renovacion_sin_lista_de_espera(self):
        p = self.uc.execute(self.prestamo.id, fecha_referencia=HOY)
        assert p.fecha_devolucion_esperada == HOY + timedelta(days=15)

    def test_renovacion_bloqueada_si_hay_reserva(self):
        reserva = Reserva(
            id=str(uuid.uuid4()),
            estudiante_id="EST-002",
            libro_id="LIB-001",
            fecha_reserva=HOY,
            estado=EstadoReserva.PENDIENTE,
        )
        self.reserva_repo.guardar(reserva)
        with pytest.raises(RenovacionBloqueadaPorReserva) as exc_info:
            self.uc.execute(self.prestamo.id, fecha_referencia=HOY)
        assert exc_info.value.libro_id == "LIB-001"

    def test_renovacion_de_libro_alta_demanda_da_3_dias(self):
        libro_ad = Libro(id="LIB-AD", titulo="SCRUM", autor="Rubin",
                         sala="Reserva", alta_demanda=True)
        self.libro_repo.guardar(libro_ad)
        ej_ad = Ejemplar(id="EJ-AD", libro_id="LIB-AD",
                         estado=EstadoEjemplar.PRESTADO)
        self.ejemplar_repo.guardar(ej_ad)
        prestamo_ad = Prestamo(
            id=str(uuid.uuid4()),
            estudiante_id="EST-003",
            ejemplar_id="EJ-AD",
            fecha_prestamo=HOY - timedelta(days=2),
            fecha_devolucion_esperada=HOY + timedelta(days=1),
            estado=EstadoPrestamo.ACTIVO,
        )
        self.prestamo_repo.guardar(prestamo_ad)
        p = self.uc.execute(prestamo_ad.id, fecha_referencia=HOY)
        assert p.fecha_devolucion_esperada == HOY + timedelta(days=3)

    def test_prestamo_inexistente_lanza_excepcion(self):
        with pytest.raises(PrestamoNoEncontrado):
            self.uc.execute("prestamo-que-no-existe")
