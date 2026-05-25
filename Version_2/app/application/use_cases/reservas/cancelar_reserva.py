from app.domain.entities.reserva import EstadoReserva
from app.domain.repositories.reserva_repository import IReservaRepository
from app.domain.exceptions import ReservaNoEncontrada


class CancelarReserva:
    def __init__(self, reserva_repo: IReservaRepository):
        self._reserva_repo = reserva_repo

    def execute(self, reserva_id: str) -> None:
        reserva = self._reserva_repo.obtener_por_id(reserva_id)
        if not reserva:
            raise ReservaNoEncontrada(reserva_id)
        reserva.estado = EstadoReserva.CANCELADA
        self._reserva_repo.actualizar(reserva)
