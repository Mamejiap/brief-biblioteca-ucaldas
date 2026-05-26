from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import List, Optional, Union
from pydantic import BaseModel
from enum import Enum

# ==================== ENUMS ====================
class EstadoPrestamo(str, Enum):
    ACTIVO = "activo"
    VENCIDO = "vencido"
    DEVUELTO = "devuelto"


class TipoEstudiante(str, Enum):
    PREGRADO = "pregrado"
    POSGRADO = "posgrado"


class EstadoEjemplar(str, Enum):
    DISPONIBLE = "disponible"
    PRESTADO = "prestado"
    DAÑADO = "dañado"


# ==================== MODELOS ====================
class Libro(BaseModel):
    id: int
    titulo: str
    autor: str
    isbn: str
    cantidad_disponible: int
    cantidad_total: int

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "titulo": "Clean Code",
                "autor": "Robert C. Martin",
                "isbn": "978-0132350884",
                "cantidad_disponible": 3,
                "cantidad_total": 5
            }
        }


class Estudiante(BaseModel):
    id: int
    nombre: str
    email: str
    carrera: str


class CrearEstudiante(BaseModel):
    id: str
    nombre: str
    programa: str
    semestre: int
    tipo: TipoEstudiante

    class Config:
        json_schema_extra = {
            "example": {
                "id": "EST-PRE-01",
                "nombre": "Ana Lopez",
                "programa": "Ingenieria de Sistemas",
                "semestre": 5,
                "tipo": "pregrado"
            }
        }


class EstudianteResponse(BaseModel):
    id: str
    nombre: str
    programa: str
    semestre: int
    tipo: str


class CrearLibro(BaseModel):
    id: str
    titulo: str
    autor: str
    sala: str
    altaDemanda: bool

    class Config:
        json_schema_extra = {
            "example": {
                "id": "LIB-001",
                "titulo": "Ingenieria del Software",
                "autor": "Pressman",
                "sala": "Sala General",
                "altaDemanda": False
            }
        }


class LibroResponse(BaseModel):
    id: str
    titulo: str
    autor: str
    sala: str
    altaDemanda: bool


class CrearEjemplar(BaseModel):
    id: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": "EJ-001-01"
            }
        }


class EjemplarResponse(BaseModel):
    id: str
    libro_id: str
    estado: str


class CrearPrestamo(BaseModel):
    estudiante_id: int
    libro_id: int
    dias_prestamo: int = 14

    class Config:
        json_schema_extra = {
            "example": {
                "estudiante_id": 1,
                "libro_id": 1,
                "dias_prestamo": 14
            }
        }


class Prestamo(BaseModel):
    id: int
    estudiante_id: int
    libro_id: int
    fecha_prestamo: str
    fecha_vencimiento: str
    fecha_devolucion: Optional[str]
    estado: EstadoPrestamo
    dias_prestamo: int

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "estudiante_id": 1,
                "libro_id": 1,
                "fecha_prestamo": "2026-05-20T10:00:00",
                "fecha_vencimiento": "2026-06-03T10:00:00",
                "fecha_devolucion": None,
                "estado": "activo",
                "dias_prestamo": 14
            }
        }


class RegistroDevoluccion(BaseModel):
    prestamo_id: int

    class Config:
        json_schema_extra = {
            "example": {
                "prestamo_id": 1
            }
        }


class PrestamosVigentes(BaseModel):
    prestamo_id: int
    estudiante_id: int
    nombre_estudiante: str
    libro_id: int
    titulo_libro: str
    fecha_prestamo: str
    fecha_vencimiento: str
    estado: EstadoPrestamo
    dias_restantes: int

    class Config:
        json_schema_extra = {
            "example": {
                "prestamo_id": 1,
                "estudiante_id": 1,
                "nombre_estudiante": "Juan Pérez",
                "libro_id": 1,
                "titulo_libro": "Clean Code",
                "fecha_prestamo": "2026-05-20T10:00:00",
                "fecha_vencimiento": "2026-06-03T10:00:00",
                "estado": "activo",
                "dias_restantes": 14
            }
        }


class ErrorResponse(BaseModel):
    error: str
    mensaje: str



# ==================== REPOSITORIO EN MEMORIA ====================
class BibliotecaRepository:
    def __init__(self):
        # Datos iniciales de libros (IDs numéricos - legacy)
        self.libros = {
            1: {
                "id": 1,
                "titulo": "Clean Code",
                "autor": "Robert C. Martin",
                "isbn": "978-0132350884",
                "cantidad_disponible": 3,
                "cantidad_total": 5
            },
            2: {
                "id": 2,
                "titulo": "Design Patterns",
                "autor": "Gang of Four",
                "isbn": "978-0201633610",
                "cantidad_disponible": 2,
                "cantidad_total": 3
            },
            3: {
                "id": 3,
                "titulo": "The Pragmatic Programmer",
                "autor": "Hunt & Thomas",
                "isbn": "978-0135957059",
                "cantidad_disponible": 4,
                "cantidad_total": 4
            }
        }

        # Nuevos libros con IDs string (del taller)
        self.libros_string = {}

        # Datos iniciales de estudiantes (IDs numéricos - legacy)
        self.estudiantes = {
            1: {
                "id": 1,
                "nombre": "Juan Pérez",
                "email": "juan.perez@ucaldas.edu.co",
                "carrera": "Ingeniería de Sistemas"
            },
            2: {
                "id": 2,
                "nombre": "María García",
                "email": "maria.garcia@ucaldas.edu.co",
                "carrera": "Ingeniería de Sistemas"
            },
            3: {
                "id": 3,
                "nombre": "Carlos López",
                "email": "carlos.lopez@ucaldas.edu.co",
                "carrera": "Administración de Empresas"
            }
        }

        # Nuevos estudiantes con IDs string (del taller)
        self.estudiantes_string = {}

        # Ejemplares individuales: { "EJ-001-01": {"id": "EJ-001-01", "libro_id": "LIB-001", "estado": "disponible"} }
        self.ejemplares = {}

        # Almacenamiento de préstamos
        self.prestamos = {}
        self.contador_prestamos = 0

    # ========== MÉTODOS PARA LIBROS (IDs int - legacy) ==========
    def obtener_todos_libros(self) -> List[dict]:
        """Obtiene la lista de todos los libros disponibles (legacy - IDs int)"""
        return list(self.libros.values())

    def obtener_libro(self, libro_id: int) -> Optional[dict]:
        """Obtiene un libro específico por ID int"""
        return self.libros.get(libro_id)

    def decrementar_disponibles(self, libro_id: int):
        """Decrementa la cantidad disponible de un libro (legacy)"""
        if self.libros[libro_id]["cantidad_disponible"] > 0:
            self.libros[libro_id]["cantidad_disponible"] -= 1
        else:
            raise ValueError("No hay ejemplares disponibles")

    def incrementar_disponibles(self, libro_id: int):
        """Incrementa la cantidad disponible de un libro (legacy)"""
        if self.libros[libro_id]["cantidad_disponible"] < self.libros[libro_id]["cantidad_total"]:
            self.libros[libro_id]["cantidad_disponible"] += 1

    # ========== MÉTODOS PARA LIBROS CON IDs STRING (nuevo) ==========
    def crear_libro(self, libro_id: str, titulo: str, autor: str, sala: str, alta_demanda: bool) -> dict:
        """Crea un nuevo libro con ID string"""
        if libro_id in self.libros_string:
            raise ValueError(f"El libro con ID {libro_id} ya existe")

        libro = {
            "id": libro_id,
            "titulo": titulo,
            "autor": autor,
            "sala": sala,
            "altaDemanda": alta_demanda
        }
        self.libros_string[libro_id] = libro
        return libro

    def obtener_libro_string(self, libro_id: str) -> Optional[dict]:
        """Obtiene un libro específico por ID string"""
        return self.libros_string.get(libro_id)

    # ========== MÉTODOS PARA ESTUDIANTES (IDs int - legacy) ==========
    def obtener_estudiante(self, estudiante_id: int) -> Optional[dict]:
        """Obtiene un estudiante específico por ID int"""
        return self.estudiantes.get(estudiante_id)

    # ========== MÉTODOS PARA ESTUDIANTES CON IDs STRING (nuevo) ==========
    def crear_estudiante(self, estudiante_id: str, nombre: str, programa: str, semestre: int, tipo: str) -> dict:
        """Crea un nuevo estudiante con ID string"""
        if estudiante_id in self.estudiantes_string:
            raise ValueError(f"El estudiante con ID {estudiante_id} ya existe")

        estudiante = {
            "id": estudiante_id,
            "nombre": nombre,
            "programa": programa,
            "semestre": semestre,
            "tipo": tipo
        }
        self.estudiantes_string[estudiante_id] = estudiante
        return estudiante

    def obtener_estudiante_string(self, estudiante_id: str) -> Optional[dict]:
        """Obtiene un estudiante específico por ID string"""
        return self.estudiantes_string.get(estudiante_id)

    # ========== MÉTODOS PARA EJEMPLARES (nuevo) ==========
    def crear_ejemplar(self, ejemplar_id: str, libro_id: str) -> dict:
        """Crea un nuevo ejemplar asociado a un libro"""
        # Verificar que el libro existe
        if libro_id not in self.libros_string:
            raise ValueError(f"El libro con ID {libro_id} no existe")

        if ejemplar_id in self.ejemplares:
            raise ValueError(f"El ejemplar con ID {ejemplar_id} ya existe")

        ejemplar = {
            "id": ejemplar_id,
            "libro_id": libro_id,
            "estado": EstadoEjemplar.DISPONIBLE
        }
        self.ejemplares[ejemplar_id] = ejemplar
        return ejemplar

    def obtener_ejemplar(self, ejemplar_id: str) -> Optional[dict]:
        """Obtiene un ejemplar específico por ID"""
        return self.ejemplares.get(ejemplar_id)

    def obtener_ejemplares_de_libro(self, libro_id: str) -> List[dict]:
        """Obtiene todos los ejemplares de un libro"""
        return [ej for ej in self.ejemplares.values() if ej["libro_id"] == libro_id]

    # ========== MÉTODOS PARA PRÉSTAMOS ==========
    def crear_prestamo(self, estudiante_id: int, libro_id: int, dias_prestamo: int) -> dict:
        """Crea un nuevo préstamo"""
        self.contador_prestamos += 1
        fecha_prestamo = datetime.now()
        fecha_vencimiento = fecha_prestamo + timedelta(days=dias_prestamo)

        prestamo = {
            "id": self.contador_prestamos,
            "estudiante_id": estudiante_id,
            "libro_id": libro_id,
            "fecha_prestamo": fecha_prestamo.isoformat(),
            "fecha_vencimiento": fecha_vencimiento.isoformat(),
            "fecha_devolucion": None,
            "estado": EstadoPrestamo.ACTIVO,
            "dias_prestamo": dias_prestamo
        }

        self.prestamos[self.contador_prestamos] = prestamo
        return prestamo

    def obtener_prestamo(self, prestamo_id: int) -> Optional[dict]:
        """Obtiene un préstamo específico por ID"""
        return self.prestamos.get(prestamo_id)

    def obtener_prestamos_vigentes(self) -> List[dict]:
        """Obtiene todos los préstamos activos o vencidos (no devueltos)"""
        prestamos_vigentes = []
        ahora = datetime.now()

        for prestamo in self.prestamos.values():
            if prestamo["estado"] != EstadoPrestamo.DEVUELTO:
                # Verificar si está vencido
                fecha_vencimiento = datetime.fromisoformat(prestamo["fecha_vencimiento"])
                if ahora > fecha_vencimiento and prestamo["estado"] == EstadoPrestamo.ACTIVO:
                    prestamo["estado"] = EstadoPrestamo.VENCIDO

                prestamos_vigentes.append(prestamo)

        return prestamos_vigentes

    def registrar_devolucion(self, prestamo_id: int) -> dict:
        """Registra la devolución de un préstamo"""
        prestamo = self.prestamos.get(prestamo_id)
        if not prestamo:
            raise ValueError("Préstamo no encontrado")

        if prestamo["estado"] == EstadoPrestamo.DEVUELTO:
            raise ValueError("Este préstamo ya fue devuelto")

        prestamo["fecha_devolucion"] = datetime.now().isoformat()
        prestamo["estado"] = EstadoPrestamo.DEVUELTO

        return prestamo


# ==================== INSTANCIA DEL REPOSITORIO ====================
repo = BibliotecaRepository()


# ==================== APLICACIÓN FASTAPI ====================
app = FastAPI(
    title="API Biblioteca UCaldas",
    description="API REST para gestionar los préstamos de libros de la biblioteca universitaria",
    version="1.0.0"
)


# ==================== ENDPOINTS - LIBROS ====================
@app.get(
    "/libros",
    response_model=List[Libro],
    summary="Listar todos los libros",
    tags=["Libros"]
)
async def listar_libros():
    """
    Obtiene la lista de todos los libros disponibles en la biblioteca
    con información sobre disponibilidad.
    """
    libros = repo.obtener_todos_libros()
    return libros


@app.post(
    "/libros",
    response_model=LibroResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo libro",
    tags=["Libros"]
)
async def crear_libro(datos: CrearLibro):
    """
    Crea un nuevo libro en la biblioteca.
    
    - **id**: ID único del libro (ej: LIB-001)
    - **titulo**: Título del libro
    - **autor**: Autor del libro
    - **sala**: Sala de ubicación (ej: Sala General, Sala de Reserva)
    - **altaDemanda**: Boolean que indica si es un libro de alta demanda
    """
    try:
        libro = repo.crear_libro(
            datos.id,
            datos.titulo,
            datos.autor,
            datos.sala,
            datos.altaDemanda
        )
        return libro
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "LIBRO_DUPLICADO",
                "mensaje": str(e)
            }
        )


@app.get(
    "/libros/{libro_id}/ejemplares",
    response_model=List[EjemplarResponse],
    summary="Listar ejemplares de un libro",
    tags=["Libros"]
)
async def listar_ejemplares(libro_id: str):
    """
    Obtiene la lista de todos los ejemplares de un libro específico.
    
    - **libro_id**: ID del libro (ej: LIB-001)
    """
    # Verificar que el libro existe
    libro = repo.obtener_libro_string(libro_id)
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "LIBRO_NO_ENCONTRADO",
                "mensaje": f"El libro con ID {libro_id} no existe"
            }
        )

    ejemplares = repo.obtener_ejemplares_de_libro(libro_id)
    return ejemplares


@app.post(
    "/libros/{libro_id}/ejemplares",
    response_model=EjemplarResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un ejemplar de un libro",
    tags=["Libros"]
)
async def crear_ejemplar(libro_id: str, datos: CrearEjemplar):
    """
    Crea un nuevo ejemplar asociado a un libro.
    
    - **libro_id**: ID del libro (ej: LIB-001)
    - **id**: ID único del ejemplar (ej: EJ-001-01)
    """
    try:
        ejemplar = repo.crear_ejemplar(datos.id, libro_id)
        return ejemplar
    except ValueError as e:
        error_msg = str(e)
        if "no existe" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "LIBRO_NO_ENCONTRADO",
                    "mensaje": error_msg
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "EJEMPLAR_DUPLICADO",
                    "mensaje": error_msg
                }
            )


# ==================== ENDPOINTS - ESTUDIANTES ====================
@app.get(
    "/estudiantes",
    response_model=List[EstudianteResponse],
    summary="Listar estudiantes",
    tags=["Estudiantes"]
)
async def listar_estudiantes():
    """
    Obtiene la lista de todos los estudiantes creados (nuevos IDs string).
    """
    estudiantes = list(repo.estudiantes_string.values())
    return estudiantes


@app.post(
    "/estudiantes",
    response_model=EstudianteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo estudiante",
    tags=["Estudiantes"]
)
async def crear_estudiante(datos: CrearEstudiante):
    """
    Crea un nuevo estudiante en el sistema.
    
    - **id**: ID único del estudiante (ej: EST-PRE-01)
    - **nombre**: Nombre del estudiante
    - **programa**: Programa académico
    - **semestre**: Semestre actual
    - **tipo**: Tipo de estudiante (pregrado o posgrado)
    """
    try:
        estudiante = repo.crear_estudiante(
            datos.id,
            datos.nombre,
            datos.programa,
            datos.semestre,
            datos.tipo.value
        )
        return estudiante
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "ESTUDIANTE_DUPLICADO",
                "mensaje": str(e)
            }
        )


# ==================== ENDPOINTS - PRÉSTAMOS ====================
@app.post(
    "/prestamos",
    response_model=Prestamo,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo préstamo",
    tags=["Préstamos"]
)
async def crear_prestamo(datos: CrearPrestamo):
    """
    Crea un nuevo préstamo para un estudiante.
    
    - **estudiante_id**: ID del estudiante que realiza el préstamo
    - **libro_id**: ID del libro a prestar
    - **dias_prestamo**: Número de días para el préstamo (por defecto 14)
    """
    # Validar que el estudiante existe
    estudiante = repo.obtener_estudiante(datos.estudiante_id)
    if not estudiante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estudiante con ID {datos.estudiante_id} no encontrado"
        )

    # Validar que el libro existe
    libro = repo.obtener_libro(datos.libro_id)
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Libro con ID {datos.libro_id} no encontrado"
        )

    # Validar que hay ejemplares disponibles
    if libro["cantidad_disponible"] <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No hay ejemplares disponibles del libro '{libro['titulo']}'"
        )

    # Validar días de préstamo
    if datos.dias_prestamo <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El número de días debe ser mayor a 0"
        )

    try:
        # Crear el préstamo
        prestamo = repo.crear_prestamo(
            datos.estudiante_id,
            datos.libro_id,
            datos.dias_prestamo
        )

        # Decrementar disponibles del libro
        repo.decrementar_disponibles(datos.libro_id)

        return prestamo
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.get(
    "/prestamos/vigentes",
    response_model=List[PrestamosVigentes],
    summary="Consultar préstamos vigentes",
    tags=["Préstamos"]
)
async def consultar_prestamos_vigentes():
    """
    Obtiene todos los préstamos que están activos o vencidos (no han sido devueltos).
    Incluye información del estudiante, del libro y días restantes para la devolución.
    """
    prestamos_vigentes = repo.obtener_prestamos_vigentes()
    resultado = []

    for prestamo in prestamos_vigentes:
        estudiante = repo.obtener_estudiante(prestamo["estudiante_id"])
        libro = repo.obtener_libro(prestamo["libro_id"])

        if estudiante and libro:
            fecha_vencimiento = datetime.fromisoformat(prestamo["fecha_vencimiento"])
            ahora = datetime.now()
            dias_restantes = (fecha_vencimiento - ahora).days

            resultado.append(PrestamosVigentes(
                prestamo_id=prestamo["id"],
                estudiante_id=estudiante["id"],
                nombre_estudiante=estudiante["nombre"],
                libro_id=libro["id"],
                titulo_libro=libro["titulo"],
                fecha_prestamo=prestamo["fecha_prestamo"],
                fecha_vencimiento=prestamo["fecha_vencimiento"],
                estado=prestamo["estado"],
                dias_restantes=dias_restantes
            ))

    return resultado


@app.post(
    "/prestamos/{prestamo_id}/devolver",
    response_model=Prestamo,
    summary="Registrar devolución de un libro",
    tags=["Préstamos"]
)
async def registrar_devolucion(prestamo_id: int):
    """
    Registra la devolución de un libro prestado.
    
    - **prestamo_id**: ID del préstamo a devolver
    """
    # Validar que el préstamo existe
    prestamo = repo.obtener_prestamo(prestamo_id)
    if not prestamo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Préstamo con ID {prestamo_id} no encontrado"
        )

    try:
        # Registrar la devolución
        prestamo_devuelto = repo.registrar_devolucion(prestamo_id)

        # Incrementar disponibles del libro
        repo.incrementar_disponibles(prestamo["libro_id"])

        return prestamo_devuelto
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )




# ==================== ENDPOINT DE BIENVENIDA ====================
@app.get(
    "/",
    summary="Endpoint de bienvenida",
    tags=["General"]
)
async def root():
    """Mensaje de bienvenida a la API"""
    return {
        "mensaje": "Bienvenido a la API de Biblioteca UCaldas",
        "version": "1.0.0",
        "documentacion": "/docs",
        "alternativa": "/redoc"
    }


# ==================== ENDPOINT DE SALUD ====================
@app.get(
    "/health",
    summary="Verificar estado de la API",
    tags=["General"]
)
async def health_check():
    """Verifica que la API está funcionando correctamente"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
