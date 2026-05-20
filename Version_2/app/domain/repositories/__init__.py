from .libro_repository import ILibroRepository, IEjemplarRepository
from .estudiante_repository import IEstudianteRepository
from .prestamo_repository import IPrestamoRepository
from .multa_repository import IMultaRepository
from .reserva_repository import IReservaRepository

__all__ = [
    "ILibroRepository",
    "IEjemplarRepository",
    "IEstudianteRepository",
    "IPrestamoRepository",
    "IMultaRepository",
    "IReservaRepository",
]
