"""
Caso de uso: Crear Reserva (lista de espera)
Un estudiante solicita un libro que actualmente esta prestado.
"""
import uuid
from dataclasses import dataclass
from datetime import date

from app.domain.entities.reserva import Reserva, EstadoReserva
from app.domain.repositories.estudiante_repository import IEstudianteRepository
from app.domain.repositories.libro_repository import ILibroRepository
from app.domain.repositories.reserva_repository import IReservaRepository
from app.domain.exceptions import (
    EstudianteNoEncontrado,
    LibroNoEncontrado,
    ReservaDuplicada,
)


@dataclass
class CrearReservaInput:
    estudiante_id: str
    libro_id: str


class CrearReserva:
    def __init__(
        self,
        estudiante_repo: IEstudianteRepository,
        libro_repo: ILibroRepository,
        reserva_repo: IReservaRepository,
    ):
        self._estudiante_repo = estudiante_repo
        self._libro_repo = libro_repo
        self._reserva_repo = reserva_repo

    def execute(self, data: CrearReservaInput) -> Reserva:
        if not self._estudiante_repo.existe(data.estudiante_id):
            raise EstudianteNoEncontrado(data.estudiante_id)

        if not self._libro_repo.existe(data.libro_id):
            raise LibroNoEncontrado(data.libro_id)

        if self._reserva_repo.existe_reserva_pendiente(data.estudiante_id, data.libro_id):
            raise ReservaDuplicada(data.estudiante_id, data.libro_id)

        reserva = Reserva(
            id=str(uuid.uuid4()),
            estudiante_id=data.estudiante_id,
            libro_id=data.libro_id,
            fecha_reserva=date.today(),
            estado=EstadoReserva.PENDIENTE,
        )
        self._reserva_repo.guardar(reserva)
        return reserva
