"""
Caso de uso: Registrar Devolución
  RN8 — si hay retraso, calcula multa = 2.000 COP × días de retraso
"""
import uuid
from dataclasses import dataclass
from datetime import date
from typing import Optional

from app.domain.entities.prestamo import EstadoPrestamo
from app.domain.entities.libro import EstadoEjemplar
from app.domain.entities.multa import Multa, TARIFA_MULTA_POR_DIA
from app.domain.repositories.prestamo_repository import IPrestamoRepository
from app.domain.repositories.libro_repository import IEjemplarRepository
from app.domain.repositories.multa_repository import IMultaRepository
from app.domain.exceptions import PrestamoNoEncontrado, PrestamoYaDevuelto


@dataclass
class DevolucionOutput:
    prestamo_id: str
    dias_retraso: int
    multa: Optional[Multa]


class RegistrarDevolucion:
    def __init__(
        self,
        prestamo_repo: IPrestamoRepository,
        ejemplar_repo: IEjemplarRepository,
        multa_repo: IMultaRepository,
    ):
        self._prestamo_repo = prestamo_repo
        self._ejemplar_repo = ejemplar_repo
        self._multa_repo = multa_repo

    def execute(self, prestamo_id: str, fecha_devolucion: Optional[date] = None) -> DevolucionOutput:
        prestamo = self._prestamo_repo.obtener_por_id(prestamo_id)
        if not prestamo:
            raise PrestamoNoEncontrado(prestamo_id)
        if prestamo.estado == EstadoPrestamo.DEVUELTO:
            raise PrestamoYaDevuelto(prestamo_id)

        hoy = fecha_devolucion or date.today()
        dias_retraso = prestamo.dias_retraso(hoy)

        # Actualizar estado del préstamo
        prestamo.fecha_devolucion_real = hoy
        prestamo.estado = EstadoPrestamo.DEVUELTO
        self._prestamo_repo.actualizar(prestamo)

        # Liberar ejemplar
        ejemplar = self._ejemplar_repo.obtener_por_id(prestamo.ejemplar_id)
        if ejemplar:
            ejemplar.estado = EstadoEjemplar.DISPONIBLE
            self._ejemplar_repo.actualizar(ejemplar)

        # RN8 — Generar multa si hubo retraso
        multa = None
        if dias_retraso > 0:
            multa = Multa(
                id=str(uuid.uuid4()),
                prestamo_id=prestamo_id,
                estudiante_id=prestamo.estudiante_id,
                monto=dias_retraso * TARIFA_MULTA_POR_DIA,
                fecha_generacion=hoy,
                pagada=False,
            )
            self._multa_repo.guardar(multa)

        return DevolucionOutput(
            prestamo_id=prestamo_id,
            dias_retraso=dias_retraso,
            multa=multa,
        )
