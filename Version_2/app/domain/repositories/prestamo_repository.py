from abc import ABC, abstractmethod
from typing import Optional
from ..entities.prestamo import Prestamo, EstadoPrestamo


class IPrestamoRepository(ABC):

    @abstractmethod
    def guardar(self, prestamo: Prestamo) -> Prestamo: ...

    @abstractmethod
    def obtener_por_id(self, prestamo_id: str) -> Optional[Prestamo]: ...

    @abstractmethod
    def actualizar(self, prestamo: Prestamo) -> Prestamo: ...

    @abstractmethod
    def listar_activos_por_estudiante(self, estudiante_id: str) -> list[Prestamo]: ...

    @abstractmethod
    def listar_por_estudiante(self, estudiante_id: str) -> list[Prestamo]: ...

    @abstractmethod
    def listar_por_estado(self, estado: EstadoPrestamo) -> list[Prestamo]: ...

    @abstractmethod
    def obtener_activo_por_ejemplar(self, ejemplar_id: str) -> Optional[Prestamo]: ...
