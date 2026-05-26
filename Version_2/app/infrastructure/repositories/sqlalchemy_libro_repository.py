"""
Implementación SQLAlchemy de ILibroRepository e IEjemplarRepository.
Convierte entre modelos ORM (LibroModel, EjemplarModel) y entidades de dominio
(Libro, Ejemplar). La lógica de negocio permanece intacta en el dominio.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities.libro import Ejemplar, EstadoEjemplar, Libro
from app.domain.repositories.libro_repository import IEjemplarRepository, ILibroRepository
from app.infrastructure.models import EjemplarModel, LibroModel


# ---------------------------------------------------------------------------
# Helpers de mapeo
# ---------------------------------------------------------------------------

def _libro_to_domain(m: LibroModel) -> Libro:
    return Libro(
        id=m.id,
        titulo=m.titulo,
        autor=m.autor,
        sala=m.sala,
        alta_demanda=m.alta_demanda,
    )


def _ejemplar_to_domain(m: EjemplarModel) -> Ejemplar:
    return Ejemplar(
        id=m.id,
        libro_id=m.libro_id,
        estado=EstadoEjemplar(m.estado),
    )


# ---------------------------------------------------------------------------
# Repositorio de Libros
# ---------------------------------------------------------------------------

class SQLAlchemyLibroRepository(ILibroRepository):
    def __init__(self, db: Session):
        self._db = db

    def guardar(self, libro: Libro) -> Libro:
        existing = self._db.get(LibroModel, libro.id)
        if existing:
            existing.titulo       = libro.titulo
            existing.autor        = libro.autor
            existing.sala         = libro.sala
            existing.alta_demanda = libro.alta_demanda
        else:
            model = LibroModel(
                id=libro.id,
                titulo=libro.titulo,
                autor=libro.autor,
                sala=libro.sala,
                alta_demanda=libro.alta_demanda,
            )
            self._db.add(model)
        self._db.commit()
        return libro

    def obtener_por_id(self, libro_id: str) -> Optional[Libro]:
        model = self._db.get(LibroModel, libro_id)
        return _libro_to_domain(model) if model else None

    def listar(
        self,
        sala: Optional[str] = None,
        alta_demanda: Optional[bool] = None,
    ) -> list[Libro]:
        query = self._db.query(LibroModel)
        if sala is not None:
            query = query.filter(LibroModel.sala == sala)
        if alta_demanda is not None:
            query = query.filter(LibroModel.alta_demanda == alta_demanda)
        return [_libro_to_domain(m) for m in query.all()]

    def existe(self, libro_id: str) -> bool:
        return self._db.get(LibroModel, libro_id) is not None


# ---------------------------------------------------------------------------
# Repositorio de Ejemplares
# ---------------------------------------------------------------------------

class SQLAlchemyEjemplarRepository(IEjemplarRepository):
    def __init__(self, db: Session):
        self._db = db

    def guardar(self, ejemplar: Ejemplar) -> Ejemplar:
        existing = self._db.get(EjemplarModel, ejemplar.id)
        if existing:
            existing.libro_id = ejemplar.libro_id
            existing.estado   = ejemplar.estado.value
        else:
            model = EjemplarModel(
                id=ejemplar.id,
                libro_id=ejemplar.libro_id,
                estado=ejemplar.estado.value,
            )
            self._db.add(model)
        self._db.commit()
        return ejemplar

    def obtener_por_id(self, ejemplar_id: str) -> Optional[Ejemplar]:
        model = self._db.get(EjemplarModel, ejemplar_id)
        return _ejemplar_to_domain(model) if model else None

    def listar_por_libro(self, libro_id: str) -> list[Ejemplar]:
        models = (
            self._db.query(EjemplarModel)
            .filter(EjemplarModel.libro_id == libro_id)
            .all()
        )
        return [_ejemplar_to_domain(m) for m in models]

    def actualizar(self, ejemplar: Ejemplar) -> Ejemplar:
        model = self._db.get(EjemplarModel, ejemplar.id)
        if model:
            model.estado = ejemplar.estado.value
            self._db.commit()
        return ejemplar
