# Biblioteca UCaldas — API REST v2

Sistema de gestión de préstamos de libros para la Universidad de Caldas.  
Stack: **Python 3.11+ · FastAPI · Pytest** · Persistencia en memoria.

---

## Levantar el servidor

```bash
# 1. Crear entorno virtual e instalar dependencias
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Arrancar
uvicorn main:app --reload
```

Servidor disponible en `http://localhost:8000`.  
Documentación interactiva: `http://localhost:8000/docs`

---

## Ejecutar los tests

```bash
pytest -v
```

---

## Endpoints principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/libros` | Listar catálogo (filtros: `sala`, `alta_demanda`, `disponible`) |
| `POST` | `/api/libros` | Crear libro |
| `GET` | `/api/libros/{id}` | Detalle de libro |
| `POST` | `/api/libros/{id}/ejemplares` | Agregar ejemplar a un libro |
| `POST` | `/api/estudiantes` | Crear estudiante |
| `GET` | `/api/estudiantes/{id}` | Detalle de estudiante |
| `GET` | `/api/estudiantes/{id}/historial` | Historial de préstamos |
| `POST` | `/api/prestamos` | Crear préstamo (evalúa RN1–RN5) |
| `GET` | `/api/prestamos/vencidos` | Listar préstamos vencidos |
| `PUT` | `/api/prestamos/{id}/devolucion` | Registrar devolución (calcula multa RN8) |
| `PUT` | `/api/prestamos/{id}/renovar` | Renovar préstamo (evalúa RN7) |
| `POST` | `/api/reservas` | Solicitar reserva de libro |
| `DELETE` | `/api/reservas/{id}` | Cancelar reserva |

---

## Reglas de negocio implementadas

| ID | Regla |
|----|-------|
| RN1 | Pregrado: máximo 3 préstamos simultáneos |
| RN2 | Posgrado: máximo 5 préstamos simultáneos |
| RN3 | Préstamo vencido pendiente bloquea nuevos préstamos |
| RN4 | Multa sin pagar bloquea nuevos préstamos |
| RN5 | Ejemplar prestado no puede prestarse de nuevo |
| RN6 | Plazo: libro normal = 15 días, alta demanda = 3 días |
| RN7 | Renovación bloqueada si hay reserva activa del libro |
| RN8 | Multa = COP 2.000 × días de retraso |

---

## Arquitectura

```
app/
├── domain/          # Entidades, interfaces de repositorio, excepciones
├── application/     # Casos de uso (lógica de negocio pura)
├── infrastructure/  # Repositorios en memoria
└── api/             # Routers FastAPI, schemas Pydantic, error handlers
```
