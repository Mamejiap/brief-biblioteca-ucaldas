from dataclasses import dataclass, field
from enum import Enum


class EstadoEjemplar(str, Enum):
    DISPONIBLE = "disponible"
    PRESTADO = "prestado"


@dataclass
class Libro:
    id: str
    titulo: str
    autor: str
    sala: str
    alta_demanda: bool = False

    @property
    def plazo_dias(self) -> int:
        """RN6: libros de alta demanda se prestan 3 días; el resto, 15 días."""
        return 3 if self.alta_demanda else 15


@dataclass
class Ejemplar:
    id: str
    libro_id: str
    estado: EstadoEjemplar = field(default=EstadoEjemplar.DISPONIBLE)

    @property
    def disponible(self) -> bool:
        return self.estado == EstadoEjemplar.DISPONIBLE
