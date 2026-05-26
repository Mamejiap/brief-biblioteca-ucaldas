from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class EstadoReserva(str, Enum):
    PENDIENTE = "pendiente"
    CANCELADA = "cancelada"
    COMPLETADA = "completada"


@dataclass
class Reserva:
    """
    Representa la solicitud de un estudiante para reservar un libro
    que actualmente esta prestado. La reserva es sobre el LIBRO
    (no sobre un ejemplar concreto), de modo que cualquier ejemplar
    del libro puede satisfacerla cuando este disponible.
    """
    id: str
    estudiante_id: str
    libro_id: str
    fecha_reserva: date
    estado: EstadoReserva = field(default=EstadoReserva.PENDIENTE)
