"""
Modelos ORM de SQLAlchemy.

IMPORTANTE: estos modelos son DISTINTOS de los dataclasses del dominio.
Su único propósito es representar las tablas de la BD.  Los repositorios
son los encargados de convertir entre modelo ORM ↔ entidad de dominio.
"""
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


# ---------------------------------------------------------------------------
# libros
# ---------------------------------------------------------------------------
class LibroModel(Base):
    __tablename__ = "libros"

    id           = Column(String, primary_key=True, index=True)
    titulo       = Column(String, nullable=False)
    autor        = Column(String, nullable=False)
    sala         = Column(String, nullable=False)
    alta_demanda = Column(Boolean, nullable=False, default=False)

    ejemplares = relationship("EjemplarModel", back_populates="libro",
                              cascade="all, delete-orphan")
    reservas   = relationship("ReservaModel",  back_populates="libro",
                              cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# ejemplares
# ---------------------------------------------------------------------------
class EjemplarModel(Base):
    __tablename__ = "ejemplares"

    id       = Column(String, primary_key=True, index=True)
    libro_id = Column(String, ForeignKey("libros.id"), nullable=False)
    estado   = Column(String, nullable=False, default="disponible")

    libro     = relationship("LibroModel",    back_populates="ejemplares")
    prestamos = relationship("PrestamoModel", back_populates="ejemplar",
                             cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# estudiantes
# ---------------------------------------------------------------------------
class EstudianteModel(Base):
    __tablename__ = "estudiantes"

    id       = Column(String, primary_key=True, index=True)
    nombre   = Column(String, nullable=False)
    programa = Column(String, nullable=False)
    semestre = Column(Integer, nullable=False)
    tipo     = Column(String, nullable=False)   # pregrado | posgrado

    prestamos = relationship("PrestamoModel", back_populates="estudiante",
                             cascade="all, delete-orphan")
    multas    = relationship("MultaModel",    back_populates="estudiante",
                             cascade="all, delete-orphan")
    reservas  = relationship("ReservaModel",  back_populates="estudiante",
                             cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# prestamos
# ---------------------------------------------------------------------------
class PrestamoModel(Base):
    __tablename__ = "prestamos"

    id                       = Column(String, primary_key=True, index=True)
    estudiante_id            = Column(String, ForeignKey("estudiantes.id"), nullable=False)
    ejemplar_id              = Column(String, ForeignKey("ejemplares.id"),  nullable=False)
    fecha_prestamo           = Column(Date, nullable=False)
    fecha_devolucion_esperada = Column(Date, nullable=False)
    fecha_devolucion_real    = Column(Date, nullable=True)
    estado                   = Column(String, nullable=False, default="activo")

    estudiante = relationship("EstudianteModel", back_populates="prestamos")
    ejemplar   = relationship("EjemplarModel",   back_populates="prestamos")
    multas     = relationship("MultaModel",       back_populates="prestamo",
                              cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# multas
# ---------------------------------------------------------------------------
class MultaModel(Base):
    __tablename__ = "multas"

    id               = Column(String, primary_key=True, index=True)
    prestamo_id      = Column(String, ForeignKey("prestamos.id"),   nullable=False)
    estudiante_id    = Column(String, ForeignKey("estudiantes.id"), nullable=False)
    monto            = Column(Integer, nullable=False)
    fecha_generacion = Column(Date, nullable=False)
    pagada           = Column(Boolean, nullable=False, default=False)

    prestamo   = relationship("PrestamoModel",   back_populates="multas")
    estudiante = relationship("EstudianteModel", back_populates="multas")


# ---------------------------------------------------------------------------
# reservas
# ---------------------------------------------------------------------------
class ReservaModel(Base):
    __tablename__ = "reservas"

    id            = Column(String, primary_key=True, index=True)
    estudiante_id = Column(String, ForeignKey("estudiantes.id"), nullable=False)
    libro_id      = Column(String, ForeignKey("libros.id"),      nullable=False)
    fecha_reserva = Column(Date, nullable=False)
    estado        = Column(String, nullable=False, default="pendiente")

    estudiante = relationship("EstudianteModel", back_populates="reservas")
    libro      = relationship("LibroModel",      back_populates="reservas")
