"""
Implementación SQLAlchemy de IEstudianteRepository.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities.estudiante import Estudiante, TipoEstudiante
from app.domain.repositories.estudiante_repository import IEstudianteRepository
from app.infrastructure.models import EstudianteModel


def _to_domain(m: EstudianteModel) -> Estudiante:
    return Estudiante(
        id=m.id,
        nombre=m.nombre,
        programa=m.programa,
        semestre=m.semestre,
        tipo=TipoEstudiante(m.tipo),
    )


class SQLAlchemyEstudianteRepository(IEstudianteRepository):
    def __init__(self, db: Session):
        self._db = db

    def guardar(self, estudiante: Estudiante) -> Estudiante:
        existing = self._db.get(EstudianteModel, estudiante.id)
        if existing:
            existing.nombre   = estudiante.nombre
            existing.programa = estudiante.programa
            existing.semestre = estudiante.semestre
            existing.tipo     = estudiante.tipo.value
        else:
            model = EstudianteModel(
                id=estudiante.id,
                nombre=estudiante.nombre,
                programa=estudiante.programa,
                semestre=estudiante.semestre,
                tipo=estudiante.tipo.value,
            )
            self._db.add(model)
        self._db.commit()
        return estudiante

    def obtener_por_id(self, estudiante_id: str) -> Optional[Estudiante]:
        model = self._db.get(EstudianteModel, estudiante_id)
        return _to_domain(model) if model else None

    def listar(self) -> list[Estudiante]:
        return [_to_domain(m) for m in self._db.query(EstudianteModel).all()]

    def existe(self, estudiante_id: str) -> bool:
        return self._db.get(EstudianteModel, estudiante_id) is not None
