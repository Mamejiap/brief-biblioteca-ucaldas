from typing import Optional
from app.domain.entities.libro import Libro, Ejemplar, EstadoEjemplar
from app.domain.repositories.libro_repository import ILibroRepository, IEjemplarRepository


class InMemoryLibroRepository(ILibroRepository):
    def __init__(self):
        self._store: dict[str, Libro] = {}

    def guardar(self, libro: Libro) -> Libro:
        self._store[libro.id] = libro
        return libro

    def obtener_por_id(self, libro_id: str) -> Optional[Libro]:
        return self._store.get(libro_id)

    def listar(
        self,
        sala: Optional[str] = None,
        alta_demanda: Optional[bool] = None,
    ) -> list[Libro]:
        result = list(self._store.values())
        if sala is not None:
            result = [l for l in result if l.sala == sala]
        if alta_demanda is not None:
            result = [l for l in result if l.alta_demanda == alta_demanda]
        return result

    def existe(self, libro_id: str) -> bool:
        return libro_id in self._store


class InMemoryEjemplarRepository(IEjemplarRepository):
    def __init__(self):
        self._store: dict[str, Ejemplar] = {}

    def guardar(self, ejemplar: Ejemplar) -> Ejemplar:
        self._store[ejemplar.id] = ejemplar
        return ejemplar

    def obtener_por_id(self, ejemplar_id: str) -> Optional[Ejemplar]:
        return self._store.get(ejemplar_id)

    def listar_por_libro(self, libro_id: str) -> list[Ejemplar]:
        return [e for e in self._store.values() if e.libro_id == libro_id]

    def actualizar(self, ejemplar: Ejemplar) -> Ejemplar:
        self._store[ejemplar.id] = ejemplar
        return ejemplar
