# API Biblioteca UCaldas - Versión 1

API REST para gestionar los préstamos de libros de la biblioteca universitaria de la Universidad de Caldas, desarrollada con **FastAPI** y almacenamiento de datos en memoria.

## Características

✅ **Listar libros** - Obtener información de todos los libros disponibles
✅ **Crear préstamos** - Registrar un nuevo préstamo de un estudiante
✅ **Consultar préstamos vigentes** - Ver todos los préstamos activos o vencidos
✅ **Registrar devoluciones** - Procesar la devolución de un libro

## Requisitos

- Python 3.9+
- pip (gestor de paquetes de Python)

## Instalación

### 1. Clonar o descargar el proyecto
```bash
cd Version_1
```

### 2. Crear un entorno virtual (recomendado)
```bash
# En Windows
python -m venv venv
venv\Scripts\activate

# En macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

## Uso

### Iniciar el servidor

```bash
python main.py
```

O usando uvicorn directamente:

```bash
uvicorn main:app --reload
```

El servidor estará disponible en: **http://localhost:8000**

### Acceder a la documentación interactiva

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints

### 📚 Libros

#### Listar todos los libros
```http
GET /libros
```

**Respuesta (200)**:
```json
[
  {
    "id": 1,
    "titulo": "Clean Code",
    "autor": "Robert C. Martin",
    "isbn": "978-0132350884",
    "cantidad_disponible": 3,
    "cantidad_total": 5
  },
  {
    "id": 2,
    "titulo": "Design Patterns",
    "autor": "Gang of Four",
    "isbn": "978-0201633610",
    "cantidad_disponible": 2,
    "cantidad_total": 3
  }
]
```

---

### 🎫 Préstamos

#### Crear un nuevo préstamo
```http
POST /prestamos
Content-Type: application/json

{
  "estudiante_id": 1,
  "libro_id": 1,
  "dias_prestamo": 14
}
```

**Respuesta (201)**:
```json
{
  "id": 1,
  "estudiante_id": 1,
  "libro_id": 1,
  "fecha_prestamo": "2026-05-20T15:30:45.123456",
  "fecha_vencimiento": "2026-06-03T15:30:45.123456",
  "fecha_devolucion": null,
  "estado": "activo",
  "dias_prestamo": 14
}
```

**Posibles errores**:
- `404`: Estudiante o libro no encontrado
- `400`: No hay ejemplares disponibles / Días inválidos

---

#### Consultar préstamos vigentes
```http
GET /prestamos/vigentes
```

**Respuesta (200)**:
```json
[
  {
    "prestamo_id": 1,
    "estudiante_id": 1,
    "nombre_estudiante": "Juan Pérez",
    "libro_id": 1,
    "titulo_libro": "Clean Code",
    "fecha_prestamo": "2026-05-20T15:30:45.123456",
    "fecha_vencimiento": "2026-06-03T15:30:45.123456",
    "estado": "activo",
    "dias_restantes": 14
  }
]
```

---

#### Registrar devolución
```http
POST /prestamos/{prestamo_id}/devolver
```

**Ejemplo**:
```http
POST /prestamos/1/devolver
```

**Respuesta (200)**:
```json
{
  "id": 1,
  "estudiante_id": 1,
  "libro_id": 1,
  "fecha_prestamo": "2026-05-20T15:30:45.123456",
  "fecha_vencimiento": "2026-06-03T15:30:45.123456",
  "fecha_devolucion": "2026-05-25T10:15:30.654321",
  "estado": "devuelto",
  "dias_prestamo": 14
}
```

**Posibles errores**:
- `404`: Préstamo no encontrado
- `400`: Préstamo ya fue devuelto

---

### 🏥 General

#### Verificar estado de la API
```http
GET /health
```

**Respuesta (200)**:
```json
{
  "status": "healthy",
  "timestamp": "2026-05-20T15:30:45.123456"
}
```

---

## Datos Iniciales

### Libros disponibles
| ID | Título | Autor | ISBN | Disponibles | Total |
|----|--------|-------|------|-------------|-------|
| 1 | Clean Code | Robert C. Martin | 978-0132350884 | 3 | 5 |
| 2 | Design Patterns | Gang of Four | 978-0201633610 | 2 | 3 |
| 3 | The Pragmatic Programmer | Hunt & Thomas | 978-0135957059 | 4 | 4 |

### Estudiantes disponibles
| ID | Nombre | Email | Carrera |
|----|--------|-------|---------|
| 1 | Juan Pérez | juan.perez@ucaldas.edu.co | Ingeniería de Sistemas |
| 2 | María García | maria.garcia@ucaldas.edu.co | Ingeniería de Sistemas |
| 3 | Carlos López | carlos.lopez@ucaldas.edu.co | Administración de Empresas |

## Flujo de Uso Típico

1. **Listar libros** → `GET /libros`
2. **Crear préstamo** → `POST /prestamos` (con estudiante_id y libro_id)
3. **Consultar vigentes** → `GET /prestamos/vigentes` (para monitoreo)
4. **Registrar devolución** → `POST /prestamos/{id}/devolver`

## Características Implementadas

### Estados de Préstamo
- **ACTIVO**: Préstamo vigente y dentro del plazo
- **VENCIDO**: Préstamo que ha superado la fecha de vencimiento
- **DEVUELTO**: Préstamo completado y libro devuelto

### Validaciones
- ✓ Verificación de existencia de estudiante y libro
- ✓ Control de disponibilidad de ejemplares
- ✓ Gestión automática de estatus (activo/vencido)
- ✓ Cálculo de días restantes
- ✓ Prevención de devoluciones duplicadas

## Estructura del Código

```
Version_1/
├── main.py              # Aplicación principal con todos los endpoints
├── requirements.txt     # Dependencias del proyecto
└── README.md           # Este archivo
```

## Desarrollo

### Extensiones Futuras

Para una versión 2 (ver carpeta `Version_2/`), se podría implementar:
- Persistencia en base de datos (SQL)
- Autenticación y autorización
- Sistema de multas por retrasos
- Notificaciones de vencimiento
- Historial de préstamos
- Reservas de libros
- Reportes y análisis

## Testing

Para hacer pruebas rápidas, puedes usar `curl`:

```bash
# Listar libros
curl http://localhost:8000/libros

# Crear préstamo
curl -X POST http://localhost:8000/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudiante_id": 1, "libro_id": 1, "dias_prestamo": 14}'

# Consultar vigentes
curl http://localhost:8000/prestamos/vigentes

# Devolver libro (reemplazar 1 con el ID real del préstamo)
curl -X POST http://localhost:8000/prestamos/1/devolver
```

## Solución de Problemas

### Puerto 8000 en uso
```bash
# Usar un puerto diferente
uvicorn main:app --port 8001
```

### Módulos no encontrados
```bash
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

## Documentación Completa

Cuando ejecutes la API, accede a:
- **Swagger UI** con validación interactiva: `http://localhost:8000/docs`
- **ReDoc** con documentación alternativa: `http://localhost:8000/redoc`

## Autor

Desarrollado como parte del brief de gestión de biblioteca - Universidad de Caldas

## Licencia

Este proyecto es de uso educativo.
