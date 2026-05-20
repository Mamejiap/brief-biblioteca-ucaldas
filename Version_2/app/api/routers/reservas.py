from fastapi import APIRouter, Depends

from app.api.dependencies import get_estudiante_repo, get_libro_repo, get_reserva_repo
from app.api.schemas import ReservaCreate, ReservaOut
from app.application.use_cases.reservas.crear_reserva import CrearReserva, CrearReservaInput
from app.application.use_cases.reservas.cancelar_reserva import CancelarReserva

router = APIRouter(prefix="/api/reservas", tags=["Reservas"])


@router.post("", response_model=ReservaOut, status_code=201)
def crear_reserva(
    body: ReservaCreate,
    estudiante_repo=Depends(get_estudiante_repo),
    libro_repo=Depends(get_libro_repo),
    reserva_repo=Depends(get_reserva_repo),
):
    uc = CrearReserva(estudiante_repo, libro_repo, reserva_repo)
    r = uc.execute(CrearReservaInput(**body.model_dump()))
    return ReservaOut(
        id=r.id,
        estudiante_id=r.estudiante_id,
        libro_id=r.libro_id,
        fecha_reserva=r.fecha_reserva,
        estado=r.estado,
    )


@router.delete("/{reserva_id}", status_code=204)
def cancelar_reserva(reserva_id: str, reserva_repo=Depends(get_reserva_repo)):
    uc = CancelarReserva(reserva_repo)
    uc.execute(reserva_id)
