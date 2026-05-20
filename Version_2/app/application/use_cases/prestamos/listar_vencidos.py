from datetime import date
from app.domain.entities.prestamo import Prestamo, EstadoPrestamo
from app.domain.repositories.prestamo_repository import IPrestamoRepository


class ListarVencidos:
    def __init__(self, prestamo_repo: IPrestamoRepository):
        self._prestamo_repo = prestamo_repo

    def execute(self) -> list[Prestamo]:
        """Devuelve todos los préstamos activos cuya fecha de devolución ya pasó."""
        hoy = date.today()
        activos = self._prestamo_repo.listar_por_estado(EstadoPrestamo.ACTIVO)
        vencidos = [p for p in activos if p.esta_vencido(hoy)]

        # Actualizar estado en repositorio para mantener consistencia
        for p in vencidos:
            if p.estado != EstadoPrestamo.VENCIDO:
                p.estado = EstadoPrestamo.VENCIDO
                self._prestamo_repo.actualizar(p)

        return vencidos
