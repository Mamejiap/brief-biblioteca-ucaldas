"""
Caso de uso: Crear Préstamo
Evalúa en orden:
  RN1/RN2 — límite de préstamos simultáneos por tipo de estudiante
  RN3     — préstamo vencido pendiente bloquea nuevos préstamos
  RN4     — multa pendiente bloquea nuevos préstamos
  RN5     — ejemplar ya prestado no puede volver a prestarse
  RN6     — plazo según tipo de libro (15 días / 3 días alta demanda)
"""
from dataclasses import dataclass
from datetime import date, timedelta

from app.domain.entities.prestamo import Prestamo, EstadoPrestamo
from app.domain.entities.libro import EstadoEjemplar
from app.domain.repositories.libro_repository import ILibroRepository, IEjemplarRepository
from app.domain.repositories.estudiante_repository import IEstudianteRepository
from app.domain.repositories.prestamo_repository import IPrestamoRepository
from app.domain.repositories.multa_repository import IMultaRepository
from app.domain.exceptions import (
    EstudianteNoEncontrado,
    EjemplarNoEncontrado,
    LibroNoEncontrado,
    LimitePrestamosAlcanzado,
    PrestamoVencidoPendiente,
    MultaPendiente,
    EjemplarNoDisponible,
)


@dataclass
class CrearPrestamoInput:
    estudiante_id: str
    ejemplar_id: str
    fecha_prestamo: date | None = None   # permite inyectar fecha en tests (ver RN3/RN4)


class CrearPrestamo:
    def __init__(
        self,
        estudiante_repo: IEstudianteRepository,
        ejemplar_repo: IEjemplarRepository,
        libro_repo: ILibroRepository,
        prestamo_repo: IPrestamoRepository,
        multa_repo: IMultaRepository,
    ):
        self._estudiante_repo = estudiante_repo
        self._ejemplar_repo = ejemplar_repo
        self._libro_repo = libro_repo
        self._prestamo_repo = prestamo_repo
        self._multa_repo = multa_repo

    def execute(self, data: CrearPrestamoInput) -> Prestamo:
        # ── Existencia ────────────────────────────────────────────────────────
        estudiante = self._estudiante_repo.obtener_por_id(data.estudiante_id)
        if not estudiante:
            raise EstudianteNoEncontrado(data.estudiante_id)

        ejemplar = self._ejemplar_repo.obtener_por_id(data.ejemplar_id)
        if not ejemplar:
            raise EjemplarNoEncontrado(data.ejemplar_id)

        libro = self._libro_repo.obtener_por_id(ejemplar.libro_id)
        if not libro:
            raise LibroNoEncontrado(ejemplar.libro_id)  # nunca debería ocurrir

        # ── RN1 / RN2 — Límite de préstamos simultáneos ───────────────────────
        activos = self._prestamo_repo.listar_activos_por_estudiante(data.estudiante_id)
        limite = estudiante.limite_prestamos
        if len(activos) >= limite:
            raise LimitePrestamosAlcanzado(data.estudiante_id, limite, len(activos))

        # ── RN3 — Préstamo vencido pendiente ──────────────────────────────────
        hoy = data.fecha_prestamo or date.today()
        vencidos = [p for p in activos if p.esta_vencido(hoy)]
        if vencidos:
            raise PrestamoVencidoPendiente(data.estudiante_id)

        # ── RN4 — Multa pendiente ─────────────────────────────────────────────
        multas_pendientes = self._multa_repo.listar_pendientes_por_estudiante(
            data.estudiante_id
        )
        if multas_pendientes:
            monto = sum(m.monto for m in multas_pendientes)
            raise MultaPendiente(data.estudiante_id, monto)

        # ── RN5 — Ejemplar disponible ─────────────────────────────────────────
        if not ejemplar.disponible:
            raise EjemplarNoDisponible(data.ejemplar_id)

        # ── RN6 — Plazo según tipo de libro ───────────────────────────────────
        fecha_devolucion_esperada = hoy + timedelta(days=libro.plazo_dias)

        # ── Crear préstamo ────────────────────────────────────────────────────
        import uuid
        prestamo = Prestamo(
            id=str(uuid.uuid4()),
            estudiante_id=data.estudiante_id,
            ejemplar_id=data.ejemplar_id,
            fecha_prestamo=hoy,
            fecha_devolucion_esperada=fecha_devolucion_esperada,
            estado=EstadoPrestamo.ACTIVO,
        )
        self._prestamo_repo.guardar(prestamo)

        # Marcar ejemplar como prestado
        ejemplar.estado = EstadoEjemplar.PRESTADO
        self._ejemplar_repo.actualizar(ejemplar)

        return prestamo
