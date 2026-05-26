# Auditoría de curls — Version_1
## Biblioteca UCaldas — Revisión Inicial

**Fecha de auditoría:** 2026-05-24  
**Versión auditada:** Version_1 (main.py)  
**Base URL:** http://localhost:8000

---

## Resumen Ejecutivo

La versión 1 actual tiene una arquitectura de **datos en memoria basada en diccionarios con IDs numéricos** (int).

Los curls del taller (`02-tu-trabajo/pruebas-reglas-negocio.md`) esperan:
- **IDs tipo string** (ej: `EST-PRE-01`, `LIB-001`, `EJ-001-01`)
- **Ejemplares individuales** con estado (`disponible`, `prestado`, etc.)
- **Conceptos adicionales:** tipo de estudiante (pregrado/posgrado), alta demanda de libros, sala de ubicación

**Resultado:** Los 3 endpoints críticos del taller **NO FUNCIONAN** actualmente.

---

## Auditoría Detallada de Endpoints

### Endpoint 1: POST /estudiantes — **FALLA ❌**

**Curl del taller:**
```bash
curl -s -X POST http://localhost:8000/estudiantes \
  -H "Content-Type: application/json" \
  -d '{
    "id": "EST-PRE-01",
    "nombre": "Ana Lopez",
    "programa": "Ingenieria de Sistemas",
    "semestre": 5,
    "tipo": "pregrado"
  }' | jq
```

**Estado actual:** `404 Not Found`

**Problema:**
- El endpoint `/estudiantes` (POST) **no existe** en Version_1
- Version_1 solo carga estudiantes estáticamente en memoria con IDs numéricos
- No hay mecanismo para crear nuevos estudiantes

**Estructura esperada en body:**
```json
{
  "id": "EST-PRE-01",        // String, patrón: EST-{TIPO}-{NUMERO}
  "nombre": "Ana Lopez",      // String
  "programa": "Ingenieria de Sistemas",  // String
  "semestre": 5,             // Integer
  "tipo": "pregrado"         // Enum: "pregrado" | "posgrado"
}
```

**Respuesta esperada:** `201 Created` + datos del estudiante creado

**Cambios mínimos propuestos:**
- Agregar modelo Pydantic `CrearEstudiante` con campos: id, nombre, programa, semestre, tipo
- Extender `BibliotecaRepository.estudiantes` para aceptar IDs string
- Implementar `POST /estudiantes` que:
  - Valide que el estudiante NO exista (409 si existe)
  - Cree el estudiante en memoria
  - Devuelva 201 + datos

---

### Endpoint 2: POST /libros — **FALLA ❌**

**Curl del taller:**
```bash
curl -s -X POST http://localhost:8000/libros \
  -H "Content-Type: application/json" \
  -d '{
    "id": "LIB-001",
    "titulo": "Ingenieria del Software",
    "autor": "Pressman",
    "sala": "Sala General",
    "altaDemanda": false
  }' | jq
```

**Estado actual:** `404 Not Found`

**Problema:**
- El endpoint `/libros` (POST) **no existe** en Version_1
- Version_1 solo carga libros estáticamente con IDs numéricos
- No hay campo `altaDemanda` ni `sala`
- El modelo actual usa `cantidad_disponible` (concepto diferente)

**Estructura esperada en body:**
```json
{
  "id": "LIB-001",            // String, patrón: LIB-{NUMERO}
  "titulo": "Ingenieria del Software",  // String
  "autor": "Pressman",        // String
  "sala": "Sala General",     // String
  "altaDemanda": false        // Boolean: impacta el plazo de préstamo
}
```

**Respuesta esperada:** `201 Created` + datos del libro creado

**Cambios mínimos propuestos:**
- Agregar modelo Pydantic `CrearLibro` con campos: id, titulo, autor, sala, altaDemanda
- Extender `BibliotecaRepository.libros` para aceptar IDs string y nuevos campos
- Implementar `POST /libros` que:
  - Valide que el libro NO exista (409 si existe)
  - Cree el libro en memoria
  - Devuelva 201 + datos

---

### Endpoint 3: POST /libros/{libro_id}/ejemplares — **FALTA ❌**

**Curl del taller:**
```bash
curl -s -X POST http://localhost:8000/libros/LIB-001/ejemplares \
  -H "Content-Type: application/json" \
  -d '{"id": "EJ-001-01"}' | jq
```

**Estado actual:** `404 Not Found`

**Problema:**
- El endpoint `/libros/{libro_id}/ejemplares` (POST) **no existe**
- Version_1 no tiene concepto de ejemplares individuales
- Usa `cantidad_disponible` y `cantidad_total` (conteo, no ejemplares con ID)
- El taller necesita ejemplares con ID único e estado individual

**Estructura esperada en body:**
```json
{
  "id": "EJ-001-01"  // String, patrón: EJ-{LIBRO_NUM}-{EJEMPLAR_NUM}
}
```

**Estructura esperada en respuesta:**
```json
{
  "id": "EJ-001-01",
  "libro_id": "LIB-001",
  "estado": "disponible"
}
```

**Cambios mínimos propuestos:**
- Agregar estructura de datos `ejemplares` en `BibliotecaRepository` como dict: `{ "EJ-001-01": {...} }`
- Cada ejemplar debe tener: id, libro_id, estado (inicialmente "disponible")
- Implementar `POST /libros/{libro_id}/ejemplares` que:
  - Valide que el libro exista (404 si no existe)
  - Valide que el ejemplar NO exista (409 si existe)
  - Cree el ejemplar en memoria
  - Devuelva 201 + datos

---

## Impacto en Endpoints Existentes

La modificación debe **mantener compatibilidad** con estos endpoints:

| Endpoint | Estado | Notas |
|----------|--------|-------|
| `GET /` | ✅ OK | Debe seguir funcionando |
| `GET /libros` | ⚠️ REVISAR | Debe devolver libros con nuevo esquema |
| `POST /prestamos` | ⚠️ REVISAR | Usará `ejemplarId` en lugar de `libro_id` |
| `GET /prestamos/vigentes` | ⚠️ REVISAR | Debe actualizar referencias |
| `POST /prestamos/{prestamo_id}/devolver` | ⚠️ REVISAR | Debe actualizar referencias |
| `GET /health` | ✅ OK | No tiene dependencias |

**Estrategia de compatibilidad:**
- Los libros existentes (ID numérico) se migran al nuevo formato
- Los IDs numéricos se aceptan como fallback temporalmente
- Los nuevos datos usan IDs string

---

## Validaciones Mínimas Requeridas

| Caso | Código HTTP | Mensaje |
|------|------------|---------|
| Crear estudiante con ID existente | `409 Conflict` | "El estudiante ya existe" |
| Crear libro con ID existente | `409 Conflict` | "El libro ya existe" |
| Crear ejemplar para libro inexistente | `404 Not Found` | "El libro no existe" |
| Crear ejemplar con ID existente | `409 Conflict` | "El ejemplar ya existe" |

---

## Formato de Errores

Todas las respuestas de error deben seguir este formato:

```json
{
  "error": "CODIGO_ERROR",
  "mensaje": "Mensaje legible para el usuario"
}
```

Ejemplos:
```json
{
  "error": "ESTUDIANTE_DUPLICADO",
  "mensaje": "El estudiante con ID EST-PRE-01 ya existe"
}
```

---

## Resultado posterior a la actualización

> *Esta sección se completará después de implementar los cambios*

### Curls que deberían funcionar:

```bash
BASE_URL="http://localhost:8000"

# ===== 1. CREAR ESTUDIANTES =====
echo "1. Crear estudiante de pregrado..."
curl -s -X POST $BASE_URL/estudiantes \
  -H "Content-Type: application/json" \
  -d '{
    "id": "EST-PRE-01",
    "nombre": "Ana Lopez",
    "programa": "Ingenieria de Sistemas",
    "semestre": 5,
    "tipo": "pregrado"
  }' | jq

echo -e "\n2. Crear estudiante de posgrado..."
curl -s -X POST $BASE_URL/estudiantes \
  -H "Content-Type: application/json" \
  -d '{
    "id": "EST-POS-01",
    "nombre": "Carlos Rios",
    "programa": "Maestria en Software",
    "semestre": 2,
    "tipo": "posgrado"
  }' | jq

# ===== 2. CREAR LIBROS =====
echo -e "\n3. Crear libro normal (15 días)..."
curl -s -X POST $BASE_URL/libros \
  -H "Content-Type: application/json" \
  -d '{
    "id": "LIB-001",
    "titulo": "Ingenieria del Software",
    "autor": "Pressman",
    "sala": "Sala General",
    "altaDemanda": false
  }' | jq

echo -e "\n4. Crear libro de alta demanda (3 días)..."
curl -s -X POST $BASE_URL/libros \
  -H "Content-Type: application/json" \
  -d '{
    "id": "LIB-002",
    "titulo": "Clean Code",
    "autor": "Martin",
    "sala": "Sala de Reserva",
    "altaDemanda": true
  }' | jq

# ===== 3. CREAR EJEMPLARES =====
echo -e "\n5. Crear ejemplares del libro LIB-001..."
for i in 01 02 03 04 05 06; do
  curl -s -X POST $BASE_URL/libros/LIB-001/ejemplares \
    -H "Content-Type: application/json" \
    -d "{\"id\": \"EJ-001-$i\"}" | jq
done

echo -e "\n6. Crear ejemplar del libro LIB-002..."
curl -s -X POST $BASE_URL/libros/LIB-002/ejemplares \
  -H "Content-Type: application/json" \
  -d '{"id": "EJ-002-01"}' | jq
```

---

## Notas técnicas

- La versión 1 mantiene datos en memoria (sin base de datos)
- No requiere implementar Clean Architecture
- Los datos se pierden al reiniciar el servidor (comportamiento normal en memoria)
- Los nuevos endpoints deben ser transaccionales internamente (sin estado compartido en requests)

