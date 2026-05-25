from fastapi import FastAPI
from app.api.routers import libros, estudiantes, prestamos, reservas
from app.api.error_handlers import register_exception_handlers
from app.database import Base, engine

# Crear todas las tablas en la BD al arrancar (si no existen ya)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Biblioteca UCaldas API",
    version="2.0.0",
    description="Sistema de gestión de préstamos de libros — Universidad de Caldas",
)

# Registrar manejadores de excepciones de dominio
register_exception_handlers(app)

# Registrar routers
app.include_router(libros.router)
app.include_router(estudiantes.router)
app.include_router(prestamos.router)
app.include_router(reservas.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": "Biblioteca UCaldas API", "version": "2.0.0"}
