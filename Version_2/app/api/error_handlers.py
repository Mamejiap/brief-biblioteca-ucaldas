"""
Mapeo de excepciones de dominio a respuestas HTTP.
"""
from fastapi import Request
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    # 404
    LibroNoEncontrado, EjemplarNoEncontrado, EstudianteNoEncontrado,
    PrestamoNoEncontrado, ReservaNoEncontrada,
    # 409
    LimitePrestamosAlcanzado, PrestamoVencidoPendiente, MultaPendiente,
    EjemplarNoDisponible, RenovacionBloqueadaPorReserva,
    PrestamoYaDevuelto, ReservaDuplicada,
    # 400
    RecursoYaExiste,
)


def register_exception_handlers(app):

    # ── 404 ───────────────────────────────────────────────────────────────────
    @app.exception_handler(LibroNoEncontrado)
    async def libro_no_encontrado(request: Request, exc: LibroNoEncontrado):
        return JSONResponse(status_code=404, content={"error": "libro_no_encontrado", "mensaje": str(exc)})

    @app.exception_handler(EjemplarNoEncontrado)
    async def ejemplar_no_encontrado(request: Request, exc: EjemplarNoEncontrado):
        return JSONResponse(status_code=404, content={"error": "ejemplar_no_encontrado", "mensaje": str(exc)})

    @app.exception_handler(EstudianteNoEncontrado)
    async def estudiante_no_encontrado(request: Request, exc: EstudianteNoEncontrado):
        return JSONResponse(status_code=404, content={"error": "estudiante_no_encontrado", "mensaje": str(exc)})

    @app.exception_handler(PrestamoNoEncontrado)
    async def prestamo_no_encontrado(request: Request, exc: PrestamoNoEncontrado):
        return JSONResponse(status_code=404, content={"error": "prestamo_no_encontrado", "mensaje": str(exc)})

    @app.exception_handler(ReservaNoEncontrada)
    async def reserva_no_encontrada(request: Request, exc: ReservaNoEncontrada):
        return JSONResponse(status_code=404, content={"error": "reserva_no_encontrada", "mensaje": str(exc)})

    # ── 409 ───────────────────────────────────────────────────────────────────
    @app.exception_handler(LimitePrestamosAlcanzado)
    async def limite_prestamos(request: Request, exc: LimitePrestamosAlcanzado):
        return JSONResponse(status_code=409, content={
            "error": "limite_prestamos_alcanzado",
            "mensaje": str(exc),
            "limite": exc.limite,
            "actuales": exc.actuales,
        })

    @app.exception_handler(PrestamoVencidoPendiente)
    async def prestamo_vencido(request: Request, exc: PrestamoVencidoPendiente):
        return JSONResponse(status_code=409, content={"error": "prestamo_vencido_pendiente", "mensaje": str(exc)})

    @app.exception_handler(MultaPendiente)
    async def multa_pendiente(request: Request, exc: MultaPendiente):
        return JSONResponse(status_code=409, content={
            "error": "multa_pendiente",
            "mensaje": str(exc),
            "monto_total": exc.monto_total,
        })

    @app.exception_handler(EjemplarNoDisponible)
    async def ejemplar_no_disponible(request: Request, exc: EjemplarNoDisponible):
        return JSONResponse(status_code=409, content={"error": "ejemplar_no_disponible", "mensaje": str(exc)})

    @app.exception_handler(RenovacionBloqueadaPorReserva)
    async def renovacion_bloqueada(request: Request, exc: RenovacionBloqueadaPorReserva):
        return JSONResponse(status_code=409, content={"error": "renovacion_bloqueada_por_reserva", "mensaje": str(exc)})

    @app.exception_handler(PrestamoYaDevuelto)
    async def prestamo_ya_devuelto(request: Request, exc: PrestamoYaDevuelto):
        return JSONResponse(status_code=409, content={"error": "prestamo_ya_devuelto", "mensaje": str(exc)})

    @app.exception_handler(ReservaDuplicada)
    async def reserva_duplicada(request: Request, exc: ReservaDuplicada):
        return JSONResponse(status_code=409, content={"error": "reserva_duplicada", "mensaje": str(exc)})

    # ── 400 ───────────────────────────────────────────────────────────────────
    @app.exception_handler(RecursoYaExiste)
    async def recurso_ya_existe(request: Request, exc: RecursoYaExiste):
        return JSONResponse(status_code=400, content={"error": "recurso_ya_existe", "mensaje": str(exc)})
