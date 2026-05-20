from typing import Optional
from app.domain.entities.multa import Multa
from app.domain.repositories.multa_repository import IMultaRepository


class InMemoryMultaRepository(IMultaRepository):
    def __init__(self):
        self._store: dict[str, Multa] = {}

    def guardar(self, multa: Multa) -> Multa:
        self._store[multa.id] = multa
        return multa

    def obtener_por_id(self, multa_id: str) -> Optional[Multa]:
        return self._store.get(multa_id)

    def actualizar(self, multa: Multa) -> Multa:
        self._store[multa.id] = multa
        return multa

    def listar_pendientes_por_estudiante(self, estudiante_id: str) -> list[Multa]:
        return [
            m for m in self._store.values()
            if m.estudiante_id == estudiante_id and not m.pagada
        ]

    def listar_por_estudiante(self, estudiante_id: str) -> list[Multa]:
        return [m for m in self._store.values() if m.estudiante_id == estudiante_id]
