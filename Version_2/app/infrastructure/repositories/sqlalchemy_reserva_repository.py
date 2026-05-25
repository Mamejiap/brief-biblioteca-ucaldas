"""
Implementación SQLAlchemy de IReservaRepository.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities.reserva import EstadoReserva, Reserva
from app.domain.repositories.reserva_repository import IReservaRepository
from app.infrastructure.models import ReservaModel


def _to_domain(m: ReservaModel) -> Reserva:
    return Reserva(
        id=m.id,
        estudiante_id=m.estudiante_id,
        libro_id=m.libro_id,
        fecha_reserva=m.fecha_reserva,
        estado=EstadoReserva(m.estado),
    )


class SQLAlchemyReservaRepository(IReservaRepository):
    def __init__(self, db: Session):
        self._db = db

    def guardar(self, reserva: Reserva) -> Reserva:
        existing = self._db.get(ReservaModel, reserva.id)
        if existing:
            existing.estudiante_id = reserva.estudiante_id
            existing.libro_id      = reserva.libro_id
            existing.fecha_reserva = reserva.fecha_reserva
            existing.estado        = reserva.estado.value
        else:
            model = ReservaModel(
                id=reserva.id,
                estudiante_id=reserva.estudiante_id,
                libro_id=reserva.libro_id,
                fecha_reserva=reserva.fecha_reserva,
                estado=reserva.estado.value,
            )
            self._db.add(model)
        self._db.commit()
        return reserva

    def obtener_por_id(self, reserva_id: str) -> Optional[Reserva]:
        model = self._db.get(ReservaModel, reserva_id)
        return _to_domain(model) if model else None

    def actualizar(self, reserva: Reserva) -> Reserva:
        return self.guardar(reserva)

    def listar_pendientes_por_libro(self, libro_id: str) -> list[Reserva]:
        models = (
            self._db.query(ReservaModel)
            .filter(
                ReservaModel.libro_id == libro_id,
                ReservaModel.estado == EstadoReserva.PENDIENTE.value,
            )
            .all()
        )
        return [_to_domain(m) for m in models]

    def listar_por_estudiante(self, estudiante_id: str) -> list[Reserva]:
        models = (
            self._db.query(ReservaModel)
            .filter(ReservaModel.estudiante_id == estudiante_id)
            .all()
        )
        return [_to_domain(m) for m in models]

    def existe_reserva_pendiente(self, estudiante_id: str, libro_id: str) -> bool:
        return (
            self._db.query(ReservaModel)
            .filter(
                ReservaModel.estudiante_id == estudiante_id,
                ReservaModel.libro_id == libro_id,
                ReservaModel.estado == EstadoReserva.PENDIENTE.value,
            )
            .first()
        ) is not None
