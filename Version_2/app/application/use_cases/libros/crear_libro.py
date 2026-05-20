from dataclasses import dataclass
from app.domain.entities.libro import Libro
from app.domain.repositories.libro_repository import ILibroRepository
from app.domain.exceptions import RecursoYaExiste


@dataclass
class CrearLibroInput:
    id: str
    titulo: str
    autor: str
    sala: str
    alta_demanda: bool = False


class CrearLibro:
    def __init__(self, repo: ILibroRepository):
        self._repo = repo

    def execute(self, data: CrearLibroInput) -> Libro:
        if self._repo.existe(data.id):
            raise RecursoYaExiste("Libro", data.id)

        libro = Libro(
            id=data.id,
            titulo=data.titulo,
            autor=data.autor,
            sala=data.sala,
            alta_demanda=data.alta_demanda,
        )
        return self._repo.guardar(libro)
