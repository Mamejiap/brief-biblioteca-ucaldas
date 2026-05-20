from app.domain.repositories.estudiante_repository import IEstudianteRepository
from app.domain.repositories.prestamo_repository import IPrestamoRepository
from app.domain.repositories.multa_repository import IMultaRepository
from app.domain.exceptions import EstudianteNoEncontrado


class ObtenerHistorial:
    def __init__(
        self,
        estudiante_repo: IEstudianteRepository,
        prestamo_repo: IPrestamoRepository,
        multa_repo: IMultaRepository,
    ):
        self._estudiante_repo = estudiante_repo
        self._prestamo_repo = prestamo_repo
        self._multa_repo = multa_repo

    def execute(self, estudiante_id: str) -> dict:
        estudiante = self._estudiante_repo.obtener_por_id(estudiante_id)
        if not estudiante:
            raise EstudianteNoEncontrado(estudiante_id)

        prestamos = self._prestamo_repo.listar_por_estudiante(estudiante_id)
        multas = self._multa_repo.listar_por_estudiante(estudiante_id)
        multas_pendientes = [m for m in multas if not m.pagada]
        monto_pendiente = sum(m.monto for m in multas_pendientes)

        return {
            "estudiante": estudiante,
            "prestamos": prestamos,
            "multas": multas,
            "monto_multas_pendientes": monto_pendiente,
        }
