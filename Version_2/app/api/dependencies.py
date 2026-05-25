"""
Inyeccion de dependencias.

Para cada request de FastAPI se abre una sesion de BD (get_db) y se construyen
los repositorios SQLAlchemy que la usan. Al terminar el request la sesion se
cierra automaticamente gracias al generador get_db().

Los repositorios en memoria (InMemory*) se conservan unicamente para la suite
de tests; no se instancian aqui.
"""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.infrastructure.repositories.sqlalchemy_libro_repository import (
    SQLAlchemyEjemplarRepository,
    SQLAlchemyLibroRepository,
)
from app.infrastructure.repositories.sqlalchemy_estudiante_repository import (
    SQLAlchemyEstudianteRepository,
)
from app.infrastructure.repositories.sqlalchemy_prestamo_repository import (
    SQLAlchemyPrestamoRepository,
)
from app.infrastructure.repositories.sqlalchemy_multa_repository import (
    SQLAlchemyMultaRepository,
)
from app.infrastructure.repositories.sqlalchemy_reserva_repository import (
    SQLAlchemyReservaRepository,
)


def get_libro_repo(db: Session = Depends(get_db)) -> SQLAlchemyLibroRepository:
    return SQLAlchemyLibroRepository(db)


def get_ejemplar_repo(db: Session = Depends(get_db)) -> SQLAlchemyEjemplarRepository:
    return SQLAlchemyEjemplarRepository(db)


def get_estudiante_repo(db: Session = Depends(get_db)) -> SQLAlchemyEstudianteRepository:
    return SQLAlchemyEstudianteRepository(db)


def get_prestamo_repo(db: Session = Depends(get_db)) -> SQLAlchemyPrestamoRepository:
    return SQLAlchemyPrestamoRepository(db)


def get_multa_repo(db: Session = Depends(get_db)) -> SQLAlchemyMultaRepository:
    return SQLAlchemyMultaRepository(db)


def get_reserva_repo(db: Session = Depends(get_db)) -> SQLAlchemyReservaRepository:
    return SQLAlchemyReservaRepository(db)
