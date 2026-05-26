"""
Fixtures compartidos por la suite de tests.
Cada fixture crea repositorios en memoria limpios para aislar cada test.
"""
import pytest
from datetime import date, timedelta

from app.domain.entities.libro import Libro, Ejemplar, EstadoEjemplar
from app.domain.entities.estudiante import Estudiante, TipoEstudiante
from app.domain.entities.prestamo import Prestamo, EstadoPrestamo
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
from app.infrastructure.repositories.in_memory_reserva_repository import (
    InMemoryReservaRepository
)


@pytest.fixture
def libro_repo():
    return InMemoryLibroRepository()

@pytest.fixture
def ejemplar_repo():
    return InMemoryEjemplarRepository()

@pytest.fixture
def estudiante_repo():
    return InMemoryEstudianteRepository()

@pytest.fixture
def prestamo_repo():
    return InMemoryPrestamoRepository()

@pytest.fixture
def multa_repo():
    return InMemoryMultaRepository()

@pytest.fixture
def reserva_repo():
    return InMemoryReservaRepository()


@pytest.fixture
def libro_normal(libro_repo):
    libro = Libro(id="LIB-001", titulo="Ingenieria del Software",
                  autor="Pressman", sala="Sala General", alta_demanda=False)
    libro_repo.guardar(libro)
    return libro

@pytest.fixture
def libro_alta_demanda(libro_repo):
    libro = Libro(id="LIB-002", titulo="Clean Code",
                  autor="Martin", sala="Sala de Reserva", alta_demanda=True)
    libro_repo.guardar(libro)
    return libro

@pytest.fixture
def ejemplar_disponible(ejemplar_repo, libro_normal):
    ej = Ejemplar(id="EJ-001-01", libro_id="LIB-001",
                  estado=EstadoEjemplar.DISPONIBLE)
    ejemplar_repo.guardar(ej)
    return ej

@pytest.fixture
def ejemplar_alta_demanda(ejemplar_repo, libro_alta_demanda):
    ej = Ejemplar(id="EJ-002-01", libro_id="LIB-002",
                  estado=EstadoEjemplar.DISPONIBLE)
    ejemplar_repo.guardar(ej)
    return ej

@pytest.fixture
def estudiante_pregrado(estudiante_repo):
    est = Estudiante(id="EST-PRE-01", nombre="Ana Lopez",
                     programa="Ingenieria de Sistemas", semestre=5,
                     tipo=TipoEstudiante.PREGRADO)
    estudiante_repo.guardar(est)
    return est

@pytest.fixture
def estudiante_posgrado(estudiante_repo):
    est = Estudiante(id="EST-POS-01", nombre="Carlos Rios",
                     programa="Maestria en Software", semestre=2,
                     tipo=TipoEstudiante.POSGRADO)
    estudiante_repo.guardar(est)
    return est
