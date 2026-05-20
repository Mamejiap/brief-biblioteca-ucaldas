from typing import Optional
from fastapi import APIRouter, Depends

from app.api.dependencies import get_libro_repo, get_ejemplar_repo
from app.api.schemas import LibroCreate, LibroOut, LibroCatalogo, LibroDetalle, EjemplarCreate, EjemplarOut
from app.application.use_cases.libros.crear_libro import CrearLibro, CrearLibroInput
from app.application.use_cases.libros.agregar_ejemplar import AgregarEjemplar, AgregarEjemplarInput
from app.application.use_cases.libros.listar_libros import ListarLibros, ObtenerLibro

router = APIRouter(prefix="/api/libros", tags=["Libros"])


@router.get("", response_model=list[LibroCatalogo])
def listar_libros(
    sala: Optional[str] = None,
    alta_demanda: Optional[bool] = None,
    disponible: Optional[bool] = None,
    libro_repo=Depends(get_libro_repo),
    ejemplar_repo=Depends(get_ejemplar_repo),
):
    uc = ListarLibros(libro_repo, ejemplar_repo)
    items = uc.execute(sala=sala, alta_demanda=alta_demanda, solo_disponibles=disponible)
    return [
        LibroCatalogo(
            id=i["libro"].id,
            titulo=i["libro"].titulo,
            autor=i["libro"].autor,
            sala=i["libro"].sala,
            alta_demanda=i["libro"].alta_demanda,
            plazo_dias=i["libro"].plazo_dias,
            total_ejemplares=i["total_ejemplares"],
            ejemplares_disponibles=i["ejemplares_disponibles"],
        )
        for i in items
    ]


@router.post("", response_model=LibroOut, status_code=201)
def crear_libro(body: LibroCreate, repo=Depends(get_libro_repo)):
    uc = CrearLibro(repo)
    libro = uc.execute(CrearLibroInput(**body.model_dump()))
    return LibroOut(
        id=libro.id,
        titulo=libro.titulo,
        autor=libro.autor,
        sala=libro.sala,
        alta_demanda=libro.alta_demanda,
        plazo_dias=libro.plazo_dias,
    )


@router.get("/{libro_id}", response_model=LibroDetalle)
def obtener_libro(
    libro_id: str,
    libro_repo=Depends(get_libro_repo),
    ejemplar_repo=Depends(get_ejemplar_repo),
):
    uc = ObtenerLibro(libro_repo, ejemplar_repo)
    data = uc.execute(libro_id)
    libro = data["libro"]
    return LibroDetalle(
        id=libro.id,
        titulo=libro.titulo,
        autor=libro.autor,
        sala=libro.sala,
        alta_demanda=libro.alta_demanda,
        plazo_dias=libro.plazo_dias,
        ejemplares=[
            EjemplarOut(id=e.id, libro_id=e.libro_id, estado=e.estado)
            for e in data["ejemplares"]
        ],
        ejemplares_disponibles=data["ejemplares_disponibles"],
    )


@router.post("/{libro_id}/ejemplares", response_model=EjemplarOut, status_code=201)
def agregar_ejemplar(
    libro_id: str,
    body: EjemplarCreate,
    libro_repo=Depends(get_libro_repo),
    ejemplar_repo=Depends(get_ejemplar_repo),
):
    uc = AgregarEjemplar(libro_repo, ejemplar_repo)
    ejemplar = uc.execute(AgregarEjemplarInput(id=body.id, libro_id=libro_id))
    return EjemplarOut(id=ejemplar.id, libro_id=ejemplar.libro_id, estado=ejemplar.estado)
