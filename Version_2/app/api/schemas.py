"""
Schemas Pydantic para request/response de la API.
Separados de las entidades de dominio para no acoplar capas.

from_attributes=True (ORM mode) se activa en todos los schemas de salida
para que Pydantic pueda leer atributos desde instancias ORM o dataclasses
de dominio indistintamente.
"""
from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities.estudiante import TipoEstudiante
from app.domain.entities.libro import EstadoEjemplar
from app.domain.entities.prestamo import EstadoPrestamo
from app.domain.entities.reserva import EstadoReserva


class _OutBase(BaseModel):
    """Base para todos los schemas de respuesta. Activa el modo ORM."""
    model_config = ConfigDict(from_attributes=True)


# ── Libro ─────────────────────────────────────────────────────────────────────

class LibroCreate(BaseModel):
    id: str = Field(..., min_length=1)
    titulo: str = Field(..., min_length=1)
    autor: str = Field(..., min_length=1)
    sala: str = Field(..., min_length=1)
    alta_demanda: bool = False

class EjemplarCreate(BaseModel):
    id: str = Field(..., min_length=1)

class EjemplarOut(_OutBase):
    id: str
    libro_id: str
    estado: EstadoEjemplar

class LibroOut(_OutBase):
    id: str
    titulo: str
    autor: str
    sala: str
    alta_demanda: bool
    plazo_dias: int

class LibroDetalle(_OutBase):
    id: str
    titulo: str
    autor: str
    sala: str
    alta_demanda: bool
    plazo_dias: int
    ejemplares: list[EjemplarOut]
    ejemplares_disponibles: int

class LibroCatalogo(_OutBase):
    id: str
    titulo: str
    autor: str
    sala: str
    alta_demanda: bool
    plazo_dias: int
    total_ejemplares: int
    ejemplares_disponibles: int


# ── Estudiante ────────────────────────────────────────────────────────────────

class EstudianteCreate(BaseModel):
    id: str = Field(..., min_length=1)
    nombre: str = Field(..., min_length=1)
    programa: str = Field(..., min_length=1)
    semestre: int = Field(..., ge=1)
    tipo: TipoEstudiante

class EstudianteOut(_OutBase):
    id: str
    nombre: str
    programa: str
    semestre: int
    tipo: TipoEstudiante
    limite_prestamos: int


# ── Préstamo ──────────────────────────────────────────────────────────────────

class PrestamoCreate(BaseModel):
    estudiante_id: str = Field(..., min_length=1)
    ejemplar_id: str = Field(..., min_length=1)
    fecha_prestamo: Optional[date] = None   # inyectable para tests

class PrestamoOut(_OutBase):
    id: str
    estudiante_id: str
    ejemplar_id: str
    fecha_prestamo: date
    fecha_devolucion_esperada: date
    fecha_devolucion_real: Optional[date]
    estado: EstadoPrestamo


# ── Multa ─────────────────────────────────────────────────────────────────────

class MultaOut(_OutBase):
    id: str
    prestamo_id: str
    estudiante_id: str
    monto: int
    fecha_generacion: date
    pagada: bool


# ── Devolución ────────────────────────────────────────────────────────────────

class DevolucionOut(_OutBase):
    prestamo_id: str
    dias_retraso: int
    multa: Optional[MultaOut]


# ── Historial ─────────────────────────────────────────────────────────────────

class HistorialOut(_OutBase):
    estudiante: EstudianteOut
    prestamos: list[PrestamoOut]
    multas: list[MultaOut]
    monto_multas_pendientes: int


# ── Reserva ───────────────────────────────────────────────────────────────────

class ReservaCreate(BaseModel):
    estudiante_id: str = Field(..., min_length=1)
    libro_id: str = Field(..., min_length=1)

class ReservaOut(_OutBase):
    id: str
    estudiante_id: str
    libro_id: str
    fecha_reserva: date
    estado: EstadoReserva
