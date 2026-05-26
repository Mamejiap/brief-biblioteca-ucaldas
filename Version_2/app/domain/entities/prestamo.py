from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


class EstadoPrestamo(str, Enum):
    ACTIVO = "activo"
    DEVUELTO = "devuelto"
    VENCIDO = "vencido"


@dataclass
class Prestamo:
    id: str
    estudiante_id: str
    ejemplar_id: str
    fecha_prestamo: date
    fecha_devolucion_esperada: date
    estado: EstadoPrestamo = field(default=EstadoPrestamo.ACTIVO)
    fecha_devolucion_real: Optional[date] = field(default=None)

    def esta_vencido(self, hoy: Optional[date] = None) -> bool:
        """Determina si el prestamo esta vencido respecto a una fecha dada."""
        referencia = hoy or date.today()
        return (
            self.estado == EstadoPrestamo.ACTIVO
            and referencia > self.fecha_devolucion_esperada
        )

    def dias_retraso(self, hoy: Optional[date] = None) -> int:
        """Dias de retraso al momento de la devolucion (0 si no hay retraso)."""
        referencia = hoy or date.today()
        if referencia > self.fecha_devolucion_esperada:
            return (referencia - self.fecha_devolucion_esperada).days
        return 0
