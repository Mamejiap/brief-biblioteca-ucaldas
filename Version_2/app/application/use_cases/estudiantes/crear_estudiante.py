from dataclasses import dataclass
from app.domain.entities.estudiante import Estudiante, TipoEstudiante
from app.domain.repositories.estudiante_repository import IEstudianteRepository
from app.domain.exceptions import RecursoYaExiste


@dataclass
class CrearEstudianteInput:
    id: str
    nombre: str
    programa: str
    semestre: int
    tipo: TipoEstudiante


class CrearEstudiante:
    def __init__(self, repo: IEstudianteRepository):
        self._repo = repo

    def execute(self, data: CrearEstudianteInput) -> Estudiante:
        if self._repo.existe(data.id):
            raise RecursoYaExiste("Estudiante", data.id)

        estudiante = Estudiante(
            id=data.id,
            nombre=data.nombre,
            programa=data.programa,
            semestre=data.semestre,
            tipo=data.tipo,
        )
        return self._repo.guardar(estudiante)
