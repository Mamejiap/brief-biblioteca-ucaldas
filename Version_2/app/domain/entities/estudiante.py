from dataclasses import dataclass
from enum import Enum


class TipoEstudiante(str, Enum):
    PREGRADO = "pregrado"
    POSGRADO = "posgrado"


# Límites de préstamos simultáneos por tipo (RN1, RN2)
LIMITE_PRESTAMOS: dict[TipoEstudiante, int] = {
    TipoEstudiante.PREGRADO: 3,
    TipoEstudiante.POSGRADO: 5,
}


@dataclass
class Estudiante:
    id: str
    nombre: str
    programa: str
    semestre: int
    tipo: TipoEstudiante

    @property
    def limite_prestamos(self) -> int:
        return LIMITE_PRESTAMOS[self.tipo]
