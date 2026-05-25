"""
Tests unitarios para el caso de uso CrearPrestamo.
Sin HTTP - prueban la logica de negocio pura.
Reglas cubiertas: RN1, RN2, RN3, RN4, RN5, RN6
"""
import uuid
import pytest
from datetime import date, timedelta

from app.application.use_cases.prestamos.crear_prestamo import (
    CrearPrestamo, CrearPrestamoInput
)
from app.domain.entities.libro import Libro, Ejemplar, EstadoEjemplar
from app.domain.entities.prestamo import Prestamo, EstadoPrestamo
from app.domain.entities.multa import Multa
from app.domain.exceptions import (
    LimitePrestamosAlcanzado,
    PrestamoVencidoPendiente,
    MultaPendiente,
    EjemplarNoDisponible,
    EstudianteNoEncontrado,
    EjemplarNoEncontrado,
)
from app.infrastructure.repositories.in_memory_libro_repository import (
    InMemoryLibroRepository, InMemoryEjemplarRepository
)
from app.infrastructure.repositories.in_memory_estudiante_repository import (
    InMemoryEstudianteRepository
)
from app.infrastructure.repositories.in_memory_prestamo_repository import (
    InMemoryPrestamoRepository
)
from app.infrastructure.repositories.in_memory_multa_repository import (
    InMemoryMultaRepository
)

HOY = date(2026, 5, 19)


def make_use_case(er, ejr, lr, pr, mr):
    return CrearPrestamo(er, ejr, lr, pr, mr)


def _agregar_ejemplares(libro_repo, ejemplar_repo, libro, n):
    ids = []
    for i in range(1, n + 1):
        ej = Ejemplar(id=f"{libro.id}-EJ-{i:02d}", libro_id=libro.id,
                      estado=EstadoEjemplar.DISPONIBLE)
        ejemplar_repo.guardar(ej)
        ids.append(ej.id)
    return ids


def _prestamo_activo(estudiante_id, ejemplar_id, repo, dias_antes=5):
    p = Prestamo(
        id=str(uuid.uuid4()),
        estudiante_id=estudiante_id,
        ejemplar_id=ejemplar_id,
        fecha_prestamo=HOY - timedelta(days=dias_antes),
        fecha_devolucion_esperada=HOY + timedelta(days=10),
        estado=EstadoPrestamo.ACTIVO,
    )
    repo.guardar(p)
    return p


class TestRN1Pregrado:
    def test_tercer_prestamo_es_valido(
        self, estudiante_pregrado, libro_normal,
        estudiante_repo, ejemplar_repo, libro_repo, prestamo_repo, multa_repo
    ):
        ejs = _agregar_ejemplares(libro_repo, ejemplar_repo, libro_normal, 3)
        _prestamo_activo(estudiante_pregrado.id, ejs[0], prestamo_repo)
        _prestamo_activo(estudiante_pregrado.id, ejs[1], prestamo_repo)
        uc = make_use_case(estudiante_repo, ejemplar_repo, libro_repo,
                           prestamo_repo, multa_repo)
        p = uc.execute(CrearPrestamoInput(
            estudiante_id=estudiante_pregrado.id,
            ejemplar_id=ejs[2], fecha_prestamo=HOY,
        ))
        assert p.estado == EstadoPrestamo.ACTIVO

    def test_cuarto_prestamo_lanza_excepcion(
        self, estudiante_pregrado, libro_normal,
        estudiante_repo, ejemplar_repo, libro_repo, prestamo_repo, multa_repo
    ):
        ejs = _agregar_ejemplares(libro_repo, ejemplar_repo, libro_normal, 4)
        for i in range(3):
            _prestamo_activo(estudiante_pregrado.id, ejs[i], prestamo_repo)
        uc = make_use_case(estudiante_repo, ejemplar_repo, libro_repo,
                           prestamo_repo, multa_repo)
        with pytest.raises(LimitePrestamosAlcanzado) as exc_info:
            uc.execute(CrearPrestamoInput(
                estudiante_id=estudiante_pregrado.id,
                ejemplar_id=ejs[3], fecha_prestamo=HOY,
            ))
        assert exc_info.value.limite == 3
        assert exc_info.value.actuales == 3


class TestRN2Posgrado:
    def test_quinto_prestamo_es_valido(
        self, estudiante_posgrado, libro_normal,
        estudiante_repo, ejemplar_repo, libro_repo, prestamo_repo, multa_repo
    ):
        ejs = _agregar_ejemplares(libro_repo, ejemplar_repo, libro_normal, 5)
        for i in range(4):
            _prestamo_activo(estudiante_posgrado.id, ejs[i], prestamo_repo)
        uc = make_use_case(estudiante_repo, ejemplar_repo, libro_repo,
                           prestamo_repo, multa_repo)
        p = uc.execute(CrearPrestamoInput(
            estudiante_id=estudiante_posgrado.id,
            ejemplar_id=ejs[4], fecha_prestamo=HOY,
        ))
        assert p.estado == EstadoPrestamo.ACTIVO

    def test_sexto_prestamo_lanza_excepcion(
        self, estudiante_posgrado, libro_normal,
        estudiante_repo, ejemplar_repo, libro_repo, prestamo_repo, multa_repo
    ):
        ejs = _agregar_ejemplares(libro_repo, ejemplar_repo, libro_normal, 6)
        for i in range(5):
            _prestamo_activo(estudiante_posgrado.id, ejs[i], prestamo_repo)
        uc = make_use_case(estudiante_repo, ejemplar_repo, libro_repo,
                           prestamo_repo, multa_repo)
        with pytest.raises(LimitePrestamosAlcanzado) as exc_info:
            uc.execute(CrearPrestamoInput(
                estudiante_id=estudiante_posgrado.id,
                ejemplar_id=ejs[5], fecha_prestamo=HOY,
            ))
        assert exc_info.value.limite == 5
        assert exc_info.value.actuales == 5


class TestRN3PrestamoVencido:
    def test_lanza_excepcion_si_hay_prestamo_vencido(
        self, estudiante_pregrado, libro_normal,
        estudiante_repo, ejemplar_repo, libro_repo, prestamo_repo, multa_repo
    ):
        ejs = _agregar_ejemplares(libro_repo, ejemplar_repo, libro_normal, 2)
        p_vencido = Prestamo(
            id=str(uuid.uuid4()),
            estudiante_id=estudiante_pregrado.id,
            ejemplar_id=ejs[0],
            fecha_prestamo=HOY - timedelta(days=20),
            fecha_devolucion_esperada=HOY - timedelta(days=5),
            estado=EstadoPrestamo.ACTIVO,
        )
        prestamo_repo.guardar(p_vencido)
        uc = make_use_case(estudiante_repo, ejemplar_repo, libro_repo,
                           prestamo_repo, multa_repo)
        with pytest.raises(PrestamoVencidoPendiente):
            uc.execute(CrearPrestamoInput(
                estudiante_id=estudiante_pregrado.id,
                ejemplar_id=ejs[1], fecha_prestamo=HOY,
            ))


class TestRN4MultaPendiente:
    def test_lanza_excepcion_si_hay_multa_pendiente(
        self, estudiante_pregrado, libro_normal,
        estudiante_repo, ejemplar_repo, libro_repo, prestamo_repo, multa_repo
    ):
        ejs = _agregar_ejemplares(libro_repo, ejemplar_repo, libro_normal, 1)
        multa = Multa(
            id=str(uuid.uuid4()),
            prestamo_id="PRESTAMO-FICTICIO",
            estudiante_id=estudiante_pregrado.id,
            monto=6_000,
            fecha_generacion=HOY - timedelta(days=3),
            pagada=False,
        )
        multa_repo.guardar(multa)
        uc = make_use_case(estudiante_repo, ejemplar_repo, libro_repo,
                           prestamo_repo, multa_repo)
        with pytest.raises(MultaPendiente) as exc_info:
            uc.execute(CrearPrestamoInput(
                estudiante_id=estudiante_pregrado.id,
                ejemplar_id=ejs[0], fecha_prestamo=HOY,
            ))
        assert exc_info.value.monto_total == 6_000


class TestRN5EjemplarNoDisponible:
    def test_lanza_excepcion_si_ejemplar_esta_prestado(
        self, estudiante_pregrado, libro_normal,
        estudiante_repo, ejemplar_repo, libro_repo, prestamo_repo, multa_repo
    ):
        ej = Ejemplar(id="EJ-PRESTADO", libro_id=libro_normal.id,
                      estado=EstadoEjemplar.PRESTADO)
        ejemplar_repo.guardar(ej)
        uc = make_use_case(estudiante_repo, ejemplar_repo, libro_repo,
                           prestamo_repo, multa_repo)
        with pytest.raises(EjemplarNoDisponible):
            uc.execute(CrearPrestamoInput(
                estudiante_id=estudiante_pregrado.id,
                ejemplar_id="EJ-PRESTADO", fecha_prestamo=HOY,
            ))


class TestRN6Plazos:
    def test_libro_normal_plazo_15_dias(
        self, estudiante_pregrado, libro_normal,
        estudiante_repo, ejemplar_repo, libro_repo, prestamo_repo, multa_repo
    ):
        ej = Ejemplar(id="EJ-N-01", libro_id=libro_normal.id,
                      estado=EstadoEjemplar.DISPONIBLE)
        ejemplar_repo.guardar(ej)
        uc = make_use_case(estudiante_repo, ejemplar_repo, libro_repo,
                           prestamo_repo, multa_repo)
        p = uc.execute(CrearPrestamoInput(
            estudiante_id=estudiante_pregrado.id,
            ejemplar_id="EJ-N-01", fecha_prestamo=HOY,
        ))
        assert p.fecha_devolucion_esperada == HOY + timedelta(days=15)

    def test_libro_alta_demanda_plazo_3_dias(
        self, estudiante_pregrado, libro_alta_demanda,
        estudiante_repo, ejemplar_repo, libro_repo, prestamo_repo, multa_repo
    ):
        ej = Ejemplar(id="EJ-AD-01", libro_id=libro_alta_demanda.id,
                      estado=EstadoEjemplar.DISPONIBLE)
        ejemplar_repo.guardar(ej)
        uc = make_use_case(estudiante_repo, ejemplar_repo, libro_repo,
                           prestamo_repo, multa_repo)
        p = uc.execute(CrearPrestamoInput(
            estudiante_id=estudiante_pregrado.id,
            ejemplar_id="EJ-AD-01", fecha_prestamo=HOY,
        ))
        assert p.fecha_devolucion_esperada == HOY + timedelta(days=3)


class TestValidaciones:
    def test_estudiante_inexistente(
        self, libro_normal,
        estudiante_repo, ejemplar_repo, libro_repo, prestamo_repo, multa_repo
    ):
        ej = Ejemplar(id="EJ-X", libro_id=libro_normal.id,
                      estado=EstadoEjemplar.DISPONIBLE)
        ejemplar_repo.guardar(ej)
        uc = make_use_case(estudiante_repo, ejemplar_repo, libro_repo,
                           prestamo_repo, multa_repo)
        with pytest.raises(EstudianteNoEncontrado):
            uc.execute(CrearPrestamoInput(
                estudiante_id="NO-EXISTE",
                ejemplar_id="EJ-X", fecha_prestamo=HOY,
            ))

    def test_ejemplar_inexistente(
        self, estudiante_pregrado,
        estudiante_repo, ejemplar_repo, libro_repo, prestamo_repo, multa_repo
    ):
        uc = make_use_case(estudiante_repo, ejemplar_repo, libro_repo,
                           prestamo_repo, multa_repo)
        with pytest.raises(EjemplarNoEncontrado):
            uc.execute(CrearPrestamoInput(
                estudiante_id=estudiante_pregrado.id,
                ejemplar_id="EJ-NO-EXISTE", fecha_prestamo=HOY,
            ))
