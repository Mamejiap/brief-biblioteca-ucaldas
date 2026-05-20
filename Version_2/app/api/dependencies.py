"""
Inyección de dependencias.
Los repositorios son singletons que viven durante toda la vida del proceso
(persistencia en memoria).
"""
from functools import lru_cache

from app.infrastructure.repositories.in_memory_libro_repository import (
    InMemoryLibroRepository,
    InMemoryEjemplarRepository,
)
from app.infrastructure.repositories.in_memory_estudiante_repository import InMemoryEstudianteRepository
from app.infrastructure.repositories.in_memory_prestamo_repository import InMemoryPrestamoRepository
from app.infrastructure.repositories.in_memory_multa_repository import InMemoryMultaRepository
from app.infrastructure.repositories.in_memory_reserva_repository import InMemoryReservaRepository


# Instancias únicas compartidas por toda la aplicación
_libro_repo = InMemoryLibroRepository()
_ejemplar_repo = InMemoryEjemplarRepository()
_estudiante_repo = InMemoryEstudianteRepository()
_prestamo_repo = InMemoryPrestamoRepository()
_multa_repo = InMemoryMultaRepository()
_reserva_repo = InMemoryReservaRepository()


def get_libro_repo() -> InMemoryLibroRepository:
    return _libro_repo

def get_ejemplar_repo() -> InMemoryEjemplarRepository:
    return _ejemplar_repo

def get_estudiante_repo() -> InMemoryEstudianteRepository:
    return _estudiante_repo

def get_prestamo_repo() -> InMemoryPrestamoRepository:
    return _prestamo_repo

def get_multa_repo() -> InMemoryMultaRepository:
    return _multa_repo

def get_reserva_repo() -> InMemoryReservaRepository:
    return _reserva_repo
