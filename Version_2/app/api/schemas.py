"""
Schemas Pydantic para request/response de la API.
Separados de las entidades de dominio para no acoplar capas.
"""
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field

from app.domain.entities.estudiante import TipoEstudiante
from app.domain.entities.libro import EstadoEjemplar
from app.domain.entities.prestamo import EstadoPrestamo
from app.domain.entities.reserva import EstadoReserva


# ── Libro ─────────────────────────────────────────────────────────────────────

class LibroCreate(BaseModel):
    id: str = Field(..., min_length=1)
    titulo: str = Field(..., min_length=1)
    autor: str = Field(..., min_length=1)
    sala: str = Field(..., min_length=1)
    alta_demanda: bool = False

class EjemplarCreate(BaseModel):
    id: str = Field(..., min_length=1)

class EjemplarOut(BaseModel):
    id: str
    libro_id: str
    estado: EstadoEjemplar

class LibroOut(BaseModel):
    id: str
    titulo: str
    autor: str
    sala: str
    alta_demanda: bool
    plazo_dias: int

class LibroDetalle(BaseModel):
    id: str
    titulo: str
    autor: str
    sala: str
    alta_demanda: bool
    plazo_dias: int
    ejemplares: list[EjemplarOut]
    ejemplares_disponibles: int

class LibroCatalogo(BaseModel):
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

class EstudianteOut(BaseModel):
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

class PrestamoOut(BaseModel):
    id: str
    estudiante_id: str
    ejemplar_id: str
    fecha_prestamo: date
    fecha_devolucion_esperada: date
    fecha_devolucion_real: Optional[date]
    estado: EstadoPrestamo


# ── Multa ─────────────────────────────────────────────────────────────────────

class MultaOut(BaseModel):
    id: str
    prestamo_id: str
    estudiante_id: str
    monto: int
    fecha_generacion: date
    pagada: bool


# ── Devolución ────────────────────────────────────────────────────────────────

class DevolucionOut(BaseModel):
    prestamo_id: str
    dias_retraso: int
    multa: Optional[MultaOut]


# ── Historial ─────────────────────────────────────────────────────────────────

class HistorialOut(BaseModel):
    estudiante: EstudianteOut
    prestamos: list[PrestamoOut]
    multas: list[MultaOut]
    monto_multas_pendientes: int


# ── Reserva ───────────────────────────────────────────────────────────────────

class ReservaCreate(BaseModel):
    estudiante_id: str = Field(..., min_length=1)
    libro_id: str = Field(..., min_length=1)

class ReservaOut(BaseModel):
    id: str
    estudiante_id: str
    libro_id: str
    fecha_reserva: date
    estado: EstadoReserva
