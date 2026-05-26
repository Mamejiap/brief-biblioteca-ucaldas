"""
Implementación SQLAlchemy de IMultaRepository.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities.multa import Multa
from app.domain.repositories.multa_repository import IMultaRepository
from app.infrastructure.models import MultaModel


def _to_domain(m: MultaModel) -> Multa:
    return Multa(
        id=m.id,
        prestamo_id=m.prestamo_id,
        estudiante_id=m.estudiante_id,
        monto=m.monto,
        fecha_generacion=m.fecha_generacion,
        pagada=m.pagada,
    )


class SQLAlchemyMultaRepository(IMultaRepository):
    def __init__(self, db: Session):
        self._db = db

    def guardar(self, multa: Multa) -> Multa:
        existing = self._db.get(MultaModel, multa.id)
        if existing:
            existing.prestamo_id      = multa.prestamo_id
            existing.estudiante_id    = multa.estudiante_id
            existing.monto            = multa.monto
            existing.fecha_generacion = multa.fecha_generacion
            existing.pagada           = multa.pagada
        else:
            model = MultaModel(
                id=multa.id,
                prestamo_id=multa.prestamo_id,
                estudiante_id=multa.estudiante_id,
                monto=multa.monto,
                fecha_generacion=multa.fecha_generacion,
                pagada=multa.pagada,
            )
            self._db.add(model)
        self._db.commit()
        return multa

    def obtener_por_id(self, multa_id: str) -> Optional[Multa]:
        model = self._db.get(MultaModel, multa_id)
        return _to_domain(model) if model else None

    def actualizar(self, multa: Multa) -> Multa:
        return self.guardar(multa)

    def listar_pendientes_por_estudiante(self, estudiante_id: str) -> list[Multa]:
        models = (
            self._db.query(MultaModel)
            .filter(
                MultaModel.estudiante_id == estudiante_id,
                MultaModel.pagada == False,  # noqa: E712
            )
            .all()
        )
        return [_to_domain(m) for m in models]

    def listar_por_estudiante(self, estudiante_id: str) -> list[Multa]:
        models = (
            self._db.query(MultaModel)
            .filter(MultaModel.estudiante_id == estudiante_id)
            .all()
        )
        return [_to_domain(m) for m in models]
