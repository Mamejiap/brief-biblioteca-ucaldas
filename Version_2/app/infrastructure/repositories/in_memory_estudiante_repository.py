from typing import Optional
from app.domain.entities.estudiante import Estudiante
from app.domain.repositories.estudiante_repository import IEstudianteRepository


class InMemoryEstudianteRepository(IEstudianteRepository):
    def __init__(self):
        self._store: dict[str, Estudiante] = {}

    def guardar(self, estudiante: Estudiante) -> Estudiante:
        self._store[estudiante.id] = estudiante
        return estudiante

    def obtener_por_id(self, estudiante_id: str) -> Optional[Estudiante]:
        return self._store.get(estudiante_id)

    def listar(self) -> list[Estudiante]:
        return list(self._store.values())

    def existe(self, estudiante_id: str) -> bool:
        return estudiante_id in self._store
