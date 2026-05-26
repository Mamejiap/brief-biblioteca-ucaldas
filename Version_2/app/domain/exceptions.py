"""
Excepciones de dominio.
Cada excepción se mapea a un código HTTP específico en la capa API.
"""


class DomainException(Exception):
    """Base para todas las excepciones de dominio."""
    pass


# ── 404 Not Found ─────────────────────────────────────────────────────────────

class LibroNoEncontrado(DomainException):
    def __init__(self, libro_id: str):
        self.libro_id = libro_id
        super().__init__(f"Libro '{libro_id}' no encontrado.")


class EjemplarNoEncontrado(DomainException):
    def __init__(self, ejemplar_id: str):
        self.ejemplar_id = ejemplar_id
        super().__init__(f"Ejemplar '{ejemplar_id}' no encontrado.")


class EstudianteNoEncontrado(DomainException):
    def __init__(self, estudiante_id: str):
        self.estudiante_id = estudiante_id
        super().__init__(f"Estudiante '{estudiante_id}' no encontrado.")


class PrestamoNoEncontrado(DomainException):
    def __init__(self, prestamo_id: str):
        self.prestamo_id = prestamo_id
        super().__init__(f"Préstamo '{prestamo_id}' no encontrado.")


class ReservaNoEncontrada(DomainException):
    def __init__(self, reserva_id: str):
        self.reserva_id = reserva_id
        super().__init__(f"Reserva '{reserva_id}' no encontrada.")


# ── 409 Conflict — Reglas de Negocio ──────────────────────────────────────────

class LimitePrestamosAlcanzado(DomainException):
    """RN1 / RN2: el estudiante alcanzó su límite de préstamos simultáneos."""
    def __init__(self, estudiante_id: str, limite: int, actuales: int):
        self.estudiante_id = estudiante_id
        self.limite = limite
        self.actuales = actuales
        super().__init__(
            f"Estudiante '{estudiante_id}' alcanzó el límite de {limite} préstamos "
            f"simultáneos (actuales: {actuales})."
        )


class PrestamoVencidoPendiente(DomainException):
    """RN3: el estudiante tiene al menos un préstamo vencido sin devolver."""
    def __init__(self, estudiante_id: str):
        self.estudiante_id = estudiante_id
        super().__init__(
            f"Estudiante '{estudiante_id}' tiene préstamos vencidos pendientes de devolución."
        )


class MultaPendiente(DomainException):
    """RN4: el estudiante tiene multas sin pagar."""
    def __init__(self, estudiante_id: str, monto_total: int):
        self.estudiante_id = estudiante_id
        self.monto_total = monto_total
        super().__init__(
            f"Estudiante '{estudiante_id}' tiene multas pendientes por ${monto_total:,} COP."
        )


class EjemplarNoDisponible(DomainException):
    """RN5: el ejemplar ya está en préstamo activo."""
    def __init__(self, ejemplar_id: str):
        self.ejemplar_id = ejemplar_id
        super().__init__(f"Ejemplar '{ejemplar_id}' no está disponible para préstamo.")


class RenovacionBloqueadaPorReserva(DomainException):
    """RN7: hay una reserva pendiente sobre el libro, no se puede renovar."""
    def __init__(self, libro_id: str):
        self.libro_id = libro_id
        super().__init__(
            f"No se puede renovar: el libro '{libro_id}' tiene estudiantes en lista de espera."
        )


class PrestamoYaDevuelto(DomainException):
    """Intento de operar sobre un préstamo que ya fue devuelto."""
    def __init__(self, prestamo_id: str):
        self.prestamo_id = prestamo_id
        super().__init__(f"El préstamo '{prestamo_id}' ya fue devuelto.")


class ReservaDuplicada(DomainException):
    """El estudiante ya tiene una reserva pendiente para ese libro."""
    def __init__(self, estudiante_id: str, libro_id: str):
        self.estudiante_id = estudiante_id
        self.libro_id = libro_id
        super().__init__(
            f"Estudiante '{estudiante_id}' ya tiene una reserva pendiente "
            f"para el libro '{libro_id}'."
        )


# ── 400 Bad Request ───────────────────────────────────────────────────────────

class RecursoYaExiste(DomainException):
    """Se intenta crear un recurso con un ID que ya existe."""
    def __init__(self, recurso: str, id_: str):
        self.recurso = recurso
        self.id_ = id_
        super().__init__(f"{recurso} con id '{id_}' ya existe.")
        self.recurso = recurso
        self.id_ = id_
        super().__init__(f"{recurso} con id '{id_}' ya existe.")
