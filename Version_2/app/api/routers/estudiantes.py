from fastapi import APIRouter, Depends

from app.api.dependencies import get_estudiante_repo, get_prestamo_repo, get_multa_repo
from app.api.schemas import EstudianteCreate, EstudianteOut, HistorialOut, MultaOut, PrestamoOut
from app.application.use_cases.estudiantes.crear_estudiante import CrearEstudiante, CrearEstudianteInput
from app.application.use_cases.estudiantes.obtener_historial import ObtenerHistorial

router = APIRouter(prefix="/api/estudiantes", tags=["Estudiantes"])


@router.post("", response_model=EstudianteOut, status_code=201)
def crear_estudiante(body: EstudianteCreate, repo=Depends(get_estudiante_repo)):
    uc = CrearEstudiante(repo)
    est = uc.execute(CrearEstudianteInput(**body.model_dump()))
    return EstudianteOut(
        id=est.id,
        nombre=est.nombre,
        programa=est.programa,
        semestre=est.semestre,
        tipo=est.tipo,
        limite_prestamos=est.limite_prestamos,
    )


@router.get("/{estudiante_id}", response_model=EstudianteOut)
def obtener_estudiante(estudiante_id: str, repo=Depends(get_estudiante_repo)):
    from app.domain.exceptions import EstudianteNoEncontrado
    est = repo.obtener_por_id(estudiante_id)
    if not est:
        raise EstudianteNoEncontrado(estudiante_id)
    return EstudianteOut(
        id=est.id, nombre=est.nombre, programa=est.programa,
        semestre=est.semestre, tipo=est.tipo, limite_prestamos=est.limite_prestamos,
    )


@router.get("/{estudiante_id}/historial", response_model=HistorialOut)
def historial(
    estudiante_id: str,
    estudiante_repo=Depends(get_estudiante_repo),
    prestamo_repo=Depends(get_prestamo_repo),
    multa_repo=Depends(get_multa_repo),
):
    uc = ObtenerHistorial(estudiante_repo, prestamo_repo, multa_repo)
    data = uc.execute(estudiante_id)
    est = data["estudiante"]
    return HistorialOut(
        estudiante=EstudianteOut(
            id=est.id, nombre=est.nombre, programa=est.programa,
            semestre=est.semestre, tipo=est.tipo, limite_prestamos=est.limite_prestamos,
        ),
        prestamos=[
            PrestamoOut(
                id=p.id, estudiante_id=p.estudiante_id, ejemplar_id=p.ejemplar_id,
                fecha_prestamo=p.fecha_prestamo,
                fecha_devolucion_esperada=p.fecha_devolucion_esperada,
                fecha_devolucion_real=p.fecha_devolucion_real,
                estado=p.estado,
            )
            for p in data["prestamos"]
        ],
        multas=[
            MultaOut(
                id=m.id, prestamo_id=m.prestamo_id, estudiante_id=m.estudiante_id,
                monto=m.monto, fecha_generacion=m.fecha_generacion, pagada=m.pagada,
            )
            for m in data["multas"]
        ],
        monto_multas_pendientes=data["monto_multas_pendientes"],
    )
