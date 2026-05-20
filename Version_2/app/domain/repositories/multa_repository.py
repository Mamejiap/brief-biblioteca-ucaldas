from abc import ABC, abstractmethod
from typing import Optional
from ..entities.multa import Multa


class IMultaRepository(ABC):

    @abstractmethod
    def guardar(self, multa: Multa) -> Multa: ...

    @abstractmethod
    def obtener_por_id(self, multa_id: str) -> Optional[Multa]: ...

    @abstractmethod
    def actualizar(self, multa: Multa) -> Multa: ...

    @abstractmethod
    def listar_pendientes_por_estudiante(self, estudiante_id: str) -> list[Multa]: ...

    @abstractmethod
    def listar_por_estudiante(self, estudiante_id: str) -> list[Multa]: ...
