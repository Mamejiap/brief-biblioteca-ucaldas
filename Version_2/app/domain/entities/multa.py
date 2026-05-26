from dataclasses import dataclass, field
from datetime import date

# RN8: tarifa fija por dia de retraso (en pesos colombianos)
TARIFA_MULTA_POR_DIA: int = 2_000


@dataclass
class Multa:
    id: str
    prestamo_id: str
    estudiante_id: str
    monto: int          # en pesos COP
    fecha_generacion: date
    pagada: bool = field(default=False)
