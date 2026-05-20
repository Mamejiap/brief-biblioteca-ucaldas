from abc import ABC, abstractmethod
from typing import Optional
from ..entities.libro import Libro, Ejemplar


class ILibroRepository(ABC):

    @abstractmethod
    def guardar(self, libro: Libro) -> Libro: ...

    @abstractmethod
    def obtener_por_id(self, libro_id: str) -> Optional[Libro]: ...

    @abstractmethod
    def listar(
        self,
        sala: Optional[str] = None,
        alta_demanda: Optional[bool] = None,
    ) -> list[Libro]: ...

    @abstractmethod
    def existe(self, libro_id: str) -> bool: ...


class IEjemplarRepository(ABC):

    @abstractmethod
    def guardar(self, ejemplar: Ejemplar) -> Ejemplar: ...

    @abstractmethod
    def obtener_por_id(self, ejemplar_id: str) -> Optional[Ejemplar]: ...

    @abstractmethod
    def listar_por_libro(self, libro_id: str) -> list[Ejemplar]: ...

    @abstractmethod
    def actualizar(self, ejemplar: Ejemplar) -> Ejemplar: ...
