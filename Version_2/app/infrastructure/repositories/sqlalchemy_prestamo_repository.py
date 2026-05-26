"""
Implementación SQLAlchemy de IPrestamoRepository.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities.prestamo import EstadoPrestamo, Prestamo
from app.domain.repositories.prestamo_repository import IPrestamoRepository
from app.infrastructure.models import PrestamoModel


def _to_domain(m: PrestamoModel) -> Prestamo:
    return Prestamo(
        id=m.id,
        estudiante_id=m.estudiante_id,
        ejemplar_id=m.ejemplar_id,
        fecha_prestamo=m.fecha_prestamo,
        fecha_devolucion_esperada=m.fecha_devolucion_esperada,
        estado=EstadoPrestamo(m.estado),
        fecha_devolucion_real=m.fecha_devolucion_real,
    )


class SQLAlchemyPrestamoRepository(IPrestamoRepository):
    def __init__(self, db: Session):
        self._db = db

    def guardar(self, prestamo: Prestamo) -> Prestamo:
        existing = self._db.get(PrestamoModel, prestamo.id)
        if existing:
            existing.estudiante_id             = prestamo.estudiante_id
            existing.ejemplar_id               = prestamo.ejemplar_id
            existing.fecha_prestamo            = prestamo.fecha_prestamo
            existing.fecha_devolucion_esperada = prestamo.fecha_devolucion_esperada
            existing.fecha_devolucion_real     = prestamo.fecha_devolucion_real
            existing.estado                    = prestamo.estado.value
        else:
            model = PrestamoModel(
                id=prestamo.id,
                estudiante_id=prestamo.estudiante_id,
                ejemplar_id=prestamo.ejemplar_id,
                fecha_prestamo=prestamo.fecha_prestamo,
                fecha_devolucion_esperada=prestamo.fecha_devolucion_esperada,
                fecha_devolucion_real=prestamo.fecha_devolucion_real,
                estado=prestamo.estado.value,
            )
            self._db.add(model)
        self._db.commit()
        return prestamo

    def obtener_por_id(self, prestamo_id: str) -> Optional[Prestamo]:
        model = self._db.get(PrestamoModel, prestamo_id)
        return _to_domain(model) if model else None

    def actualizar(self, prestamo: Prestamo) -> Prestamo:
        # guardar maneja tanto insert como update
        return self.guardar(prestamo)

    def listar_activos_por_estudiante(self, estudiante_id: str) -> list[Prestamo]:
        models = (
            self._db.query(PrestamoModel)
            .filter(
                PrestamoModel.estudiante_id == estudiante_id,
                PrestamoModel.estado == EstadoPrestamo.ACTIVO.value,
            )
            .all()
        )
        return [_to_domain(m) for m in models]

    def listar_por_estudiante(self, estudiante_id: str) -> list[Prestamo]:
        models = (
            self._db.query(PrestamoModel)
            .filter(PrestamoModel.estudiante_id == estudiante_id)
            .all()
        )
        return [_to_domain(m) for m in models]

    def listar_por_estado(self, estado: EstadoPrestamo) -> list[Prestamo]:
        models = (
            self._db.query(PrestamoModel)
            .filter(PrestamoModel.estado == estado.value)
            .all()
        )
        return [_to_domain(m) for m in models]

    def obtener_activo_por_ejemplar(self, ejemplar_id: str) -> Optional[Prestamo]:
        model = (
            self._db.query(PrestamoModel)
            .filter(
                PrestamoModel.ejemplar_id == ejemplar_id,
                PrestamoModel.estado == EstadoPrestamo.ACTIVO.value,
            )
            .first()
        )
        return _to_domain(model) if model else None
