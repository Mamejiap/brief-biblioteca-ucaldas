from abc import ABC, abstractmethod
from typing import Optional
from ..entities.reserva import Reserva, EstadoReserva


class IReservaRepository(ABC):

    @abstractmethod
    def guardar(self, reserva: Reserva) -> Reserva: ...

    @abstractmethod
    def obtener_por_id(self, reserva_id: str) -> Optional[Reserva]: ...

    @abstractmethod
    def actualizar(self, reserva: Reserva) -> Reserva: ...

    @abstractmethod
    def listar_pendientes_por_libro(self, libro_id: str) -> list[Reserva]: ...

    @abstractmethod
    def listar_por_estudiante(self, estudiante_id: str) -> list[Reserva]: ...

    @abstractmethod
    def existe_reserva_pendiente(self, estudiante_id: str, libro_id: str) -> bool: ...
