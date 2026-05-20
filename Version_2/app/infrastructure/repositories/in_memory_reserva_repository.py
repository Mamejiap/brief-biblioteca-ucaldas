from typing import Optional
from app.domain.entities.reserva import Reserva, EstadoReserva
from app.domain.repositories.reserva_repository import IReservaRepository


class InMemoryReservaRepository(IReservaRepository):
    def __init__(self):
        self._store: dict[str, Reserva] = {}

    def guardar(self, reserva: Reserva) -> Reserva:
        self._store[reserva.id] = reserva
        return reserva

    def obtener_por_id(self, reserva_id: str) -> Optional[Reserva]:
        return self._store.get(reserva_id)

    def actualizar(self, reserva: Reserva) -> Reserva:
        self._store[reserva.id] = reserva
        return reserva

    def listar_pendientes_por_libro(self, libro_id: str) -> list[Reserva]:
        return [
            r for r in self._store.values()
            if r.libro_id == libro_id and r.estado == EstadoReserva.PENDIENTE
        ]

    def listar_por_estudiante(self, estudiante_id: str) -> list[Reserva]:
        return [r for r in self._store.values() if r.estudiante_id == estudiante_id]

    def existe_reserva_pendiente(self, estudiante_id: str, libro_id: str) -> bool:
        return any(
            r for r in self._store.values()
            if r.estudiante_id == estudiante_id
            and r.libro_id == libro_id
            and r.estado == EstadoReserva.PENDIENTE
        )
