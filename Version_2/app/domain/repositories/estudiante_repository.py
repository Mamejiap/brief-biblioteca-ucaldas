from abc import ABC, abstractmethod
from typing import Optional
from ..entities.estudiante import Estudiante


class IEstudianteRepository(ABC):

    @abstractmethod
    def guardar(self, estudiante: Estudiante) -> Estudiante: ...

    @abstractmethod
    def obtener_por_id(self, estudiante_id: str) -> Optional[Estudiante]: ...

    @abstractmethod
    def listar(self) -> list[Estudiante]: ...

    @abstractmethod
    def existe(self, estudiante_id: str) -> bool: ...
