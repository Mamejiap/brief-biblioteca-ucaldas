from dataclasses import dataclass
from app.domain.entities.libro import Ejemplar, EstadoEjemplar
from app.domain.repositories.libro_repository import ILibroRepository, IEjemplarRepository
from app.domain.exceptions import LibroNoEncontrado, RecursoYaExiste


@dataclass
class AgregarEjemplarInput:
    id: str
    libro_id: str


class AgregarEjemplar:
    def __init__(self, libro_repo: ILibroRepository, ejemplar_repo: IEjemplarRepository):
        self._libro_repo = libro_repo
        self._ejemplar_repo = ejemplar_repo

    def execute(self, data: AgregarEjemplarInput) -> Ejemplar:
        if not self._libro_repo.existe(data.libro_id):
            raise LibroNoEncontrado(data.libro_id)

        if self._ejemplar_repo.obtener_por_id(data.id):
            raise RecursoYaExiste("Ejemplar", data.id)

        ejemplar = Ejemplar(
            id=data.id,
            libro_id=data.libro_id,
            estado=EstadoEjemplar.DISPONIBLE,
        )
        return self._ejemplar_repo.guardar(ejemplar)
