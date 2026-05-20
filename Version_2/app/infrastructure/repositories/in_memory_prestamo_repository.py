from typing import Optional
from app.domain.entities.prestamo import Prestamo, EstadoPrestamo
from app.domain.repositories.prestamo_repository import IPrestamoRepository


class InMemoryPrestamoRepository(IPrestamoRepository):
    def __init__(self):
        self._store: dict[str, Prestamo] = {}

    def guardar(self, prestamo: Prestamo) -> Prestamo:
        self._store[prestamo.id] = prestamo
        return prestamo

    def obtener_por_id(self, prestamo_id: str) -> Optional[Prestamo]:
        return self._store.get(prestamo_id)

    def actualizar(self, prestamo: Prestamo) -> Prestamo:
        self._store[prestamo.id] = prestamo
        return prestamo

    def listar_activos_por_estudiante(self, estudiante_id: str) -> list[Prestamo]:
        return [
            p for p in self._store.values()
            if p.estudiante_id == estudiante_id and p.estado == EstadoPrestamo.ACTIVO
        ]

    def listar_por_estudiante(self, estudiante_id: str) -> list[Prestamo]:
        return [
            p for p in self._store.values()
            if p.estudiante_id == estudiante_id
        ]

    def listar_por_estado(self, estado: EstadoPrestamo) -> list[Prestamo]:
        return [p for p in self._store.values() if p.estado == estado]

    def obtener_activo_por_ejemplar(self, ejemplar_id: str) -> Optional[Prestamo]:
        return next(
            (
                p for p in self._store.values()
                if p.ejemplar_id == ejemplar_id and p.estado == EstadoPrestamo.ACTIVO
            ),
            None,
        )
