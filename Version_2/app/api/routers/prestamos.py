from fastapi import APIRouter, Depends

from app.api.dependencies import (
    get_estudiante_repo, get_ejemplar_repo, get_libro_repo,
    get_prestamo_repo, get_multa_repo, get_reserva_repo,
)
from app.api.schemas import PrestamoCreate, PrestamoOut, DevolucionOut, MultaOut
from app.application.use_cases.prestamos.crear_prestamo import CrearPrestamo, CrearPrestamoInput
from app.application.use_cases.prestamos.registrar_devolucion import RegistrarDevolucion
from app.application.use_cases.prestamos.renovar_prestamo import RenovarPrestamo
from app.application.use_cases.prestamos.listar_vencidos import ListarVencidos

router = APIRouter(prefix="/api/prestamos", tags=["Prestamos"])


def _prestamo_out(p) -> PrestamoOut:
    return PrestamoOut(
        id=p.id,
        estudiante_id=p.estudiante_id,
        ejemplar_id=p.ejemplar_id,
        fecha_prestamo=p.fecha_prestamo,
        fecha_devolucion_esperada=p.fecha_devolucion_esperada,
        fecha_devolucion_real=p.fecha_devolucion_real,
        estado=p.estado,
    )


@router.post("", response_model=PrestamoOut, status_code=201)
def crear_prestamo(
    body: PrestamoCreate,
    estudiante_repo=Depends(get_estudiante_repo),
    ejemplar_repo=Depends(get_ejemplar_repo),
    libro_repo=Depends(get_libro_repo),
    prestamo_repo=Depends(get_prestamo_repo),
    multa_repo=Depends(get_multa_repo),
):
    uc = CrearPrestamo(estudiante_repo, ejemplar_repo, libro_repo, prestamo_repo, multa_repo)
    prestamo = uc.execute(CrearPrestamoInput(**body.model_dump()))
    return _prestamo_out(prestamo)


@router.get("/vencidos", response_model=list[PrestamoOut])
def listar_vencidos(prestamo_repo=Depends(get_prestamo_repo)):
    uc = ListarVencidos(prestamo_repo)
    return [_prestamo_out(p) for p in uc.execute()]


@router.get("/{prestamo_id}", response_model=PrestamoOut)
def obtener_prestamo(prestamo_id: str, prestamo_repo=Depends(get_prestamo_repo)):
    from app.domain.exceptions import PrestamoNoEncontrado
    p = prestamo_repo.obtener_por_id(prestamo_id)
    if not p:
        raise PrestamoNoEncontrado(prestamo_id)
    return _prestamo_out(p)


@router.put("/{prestamo_id}/devolucion", response_model=DevolucionOut)
def registrar_devolucion(
    prestamo_id: str,
    prestamo_repo=Depends(get_prestamo_repo),
    ejemplar_repo=Depends(get_ejemplar_repo),
    multa_repo=Depends(get_multa_repo),
):
    uc = RegistrarDevolucion(prestamo_repo, ejemplar_repo, multa_repo)
    result = uc.execute(prestamo_id)
    multa_out = None
    if result.multa:
        m = result.multa
        multa_out = MultaOut(
            id=m.id, prestamo_id=m.prestamo_id, estudiante_id=m.estudiante_id,
            monto=m.monto, fecha_generacion=m.fecha_generacion, pagada=m.pagada,
        )
    return DevolucionOut(
        prestamo_id=result.prestamo_id,
        dias_retraso=result.dias_retraso,
        multa=multa_out,
    )


@router.put("/{prestamo_id}/renovar", response_model=PrestamoOut)
def renovar_prestamo(
    prestamo_id: str,
    prestamo_repo=Depends(get_prestamo_repo),
    ejemplar_repo=Depends(get_ejemplar_repo),
    libro_repo=Depends(get_libro_repo),
    reserva_repo=Depends(get_reserva_repo),
):
    uc = RenovarPrestamo(prestamo_repo, ejemplar_repo, libro_repo, reserva_repo)
    prestamo = uc.execute(prestamo_id)
    return _prestamo_out(prestamo)
