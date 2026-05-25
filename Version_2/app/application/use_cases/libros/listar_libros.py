from typing import Optional
from app.domain.repositories.libro_repository import ILibroRepository, IEjemplarRepository


class ListarLibros:
    def __init__(self, libro_repo: ILibroRepository, ejemplar_repo: IEjemplarRepository):
        self._libro_repo = libro_repo
        self._ejemplar_repo = ejemplar_repo

    def execute(
        self,
        sala: Optional[str] = None,
        alta_demanda: Optional[bool] = None,
        solo_disponibles: Optional[bool] = None,
    ) -> list[dict]:
        libros = self._libro_repo.listar(sala=sala, alta_demanda=alta_demanda)

        resultado = []
        for libro in libros:
            ejemplares = self._ejemplar_repo.listar_por_libro(libro.id)
            disponibles = sum(1 for e in ejemplares if e.disponible)

            if solo_disponibles and disponibles == 0:
                continue

            resultado.append({
                "libro": libro,
                "total_ejemplares": len(ejemplares),
                "ejemplares_disponibles": disponibles,
            })

        return resultado


class ObtenerLibro:
    def __init__(self, libro_repo: ILibroRepository, ejemplar_repo: IEjemplarRepository):
        self._libro_repo = libro_repo
        self._ejemplar_repo = ejemplar_repo

    def execute(self, libro_id: str) -> dict:
        from app.domain.exceptions import LibroNoEncontrado
        libro = self._libro_repo.obtener_por_id(libro_id)
        if not libro:
            raise LibroNoEncontrado(libro_id)

        ejemplares = self._ejemplar_repo.listar_por_libro(libro_id)
        disponibles = sum(1 for e in ejemplares if e.disponible)

        return {
            "libro": libro,
            "ejemplares": ejemplares,
            "ejemplares_disponibles": disponibles,
        }
