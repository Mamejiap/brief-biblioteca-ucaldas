"""
Caso de uso: Renovar Prestamo
  RN7 - si hay reservas pendientes para el libro, la renovacion se deniega
  RN6 - el nuevo plazo usa las mismas reglas (15 dias o 3 dias si alta demanda)
"""
from datetime import timedelta, date
from typing import Optional

from app.domain.entities.prestamo import EstadoPrestamo
from app.domain.repositories.prestamo_repository import IPrestamoRepository
from app.domain.repositories.libro_repository import ILibroRepository, IEjemplarRepository
from app.domain.repositories.reserva_repository import IReservaRepository
from app.domain.exceptions import (
    PrestamoNoEncontrado,
    PrestamoYaDevuelto,
    RenovacionBloqueadaPorReserva,
    EjemplarNoEncontrado,
    LibroNoEncontrado,
)


class RenovarPrestamo:
    def __init__(
        self,
        prestamo_repo: IPrestamoRepository,
        ejemplar_repo: IEjemplarRepository,
        libro_repo: ILibroRepository,
        reserva_repo: IReservaRepository,
    ):
        self._prestamo_repo = prestamo_repo
        self._ejemplar_repo = ejemplar_repo
        self._libro_repo = libro_repo
        self._reserva_repo = reserva_repo

    def execute(self, prestamo_id: str, fecha_referencia: Optional[date] = None):
        prestamo = self._prestamo_repo.obtener_por_id(prestamo_id)
        if not prestamo:
            raise PrestamoNoEncontrado(prestamo_id)
        if prestamo.estado == EstadoPrestamo.DEVUELTO:
            raise PrestamoYaDevuelto(prestamo_id)

        ejemplar = self._ejemplar_repo.obtener_por_id(prestamo.ejemplar_id)
        if not ejemplar:
            raise EjemplarNoEncontrado(prestamo.ejemplar_id)

        libro = self._libro_repo.obtener_por_id(ejemplar.libro_id)
        if not libro:
            raise LibroNoEncontrado(ejemplar.libro_id)

        reservas = self._reserva_repo.listar_pendientes_por_libro(libro.id)
        if reservas:
            raise RenovacionBloqueadaPorReserva(libro.id)

        hoy = fecha_referencia or date.today()
        prestamo.fecha_devolucion_esperada = hoy + timedelta(days=libro.plazo_dias)
        prestamo.estado = EstadoPrestamo.ACTIVO
        self._prestamo_repo.actualizar(prestamo)
        return prestamo
