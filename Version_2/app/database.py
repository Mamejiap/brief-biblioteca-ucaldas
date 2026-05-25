"""
Configuración de la base de datos SQLite con SQLAlchemy 2.0.
Este módulo es el único punto de contacto con el motor de BD;
el resto de la aplicación lo consume a través de get_db().
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Ruta del archivo SQLite (relativa al directorio de ejecución del proceso)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./biblioteca.db")

# check_same_thread=False es obligatorio para SQLite cuando se usa con FastAPI
# (los requests pueden ejecutarse en hilos distintos al que abrió la conexión).
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,          # Cambiar a True para ver SQL en consola durante depuración
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """Clase base para todos los modelos ORM de la aplicación."""
    pass


def get_db():
    """
    Dependencia de FastAPI que provee una sesión de BD por request.
    La sesión se cierra automáticamente al terminar el request,
    incluso si ocurre una excepción.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
