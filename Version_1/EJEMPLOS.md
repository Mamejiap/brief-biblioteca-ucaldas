# Ejemplos de Uso - API Biblioteca UCaldas v1

Este archivo contiene ejemplos prácticos de cómo usar la API con diferentes herramientas.

## Opción 1: Usar Swagger UI (Recomendado para principiantes)

1. Inicia el servidor: `python main.py`
2. Abre en tu navegador: http://localhost:8000/docs
3. Haz clic en cada endpoint para expandirlo
4. Haz clic en "Try it out"
5. Completa los campos requeridos
6. Haz clic en "Execute"

## Opción 2: Usar la extensión REST Client en VS Code

1. Instala la extensión "REST Client" de Huachao Mao
2. Abre el archivo `requests.http`
3. Haz clic en "Send Request" sobre cada petición
4. Verás la respuesta en una nueva pestaña

## Opción 3: Usar curl desde terminal

### Ejemplo 1: Listar todos los libros

```bash
curl http://localhost:8000/libros
```

**Respuesta:**
```json
[
  {
    "id": 1,
    "titulo": "Clean Code",
    "autor": "Robert C. Martin",
    "isbn": "978-0132350884",
    "cantidad_disponible": 3,
    "cantidad_total": 5
  }
]
```

### Ejemplo 2: Crear un préstamo

```bash
curl -X POST http://localhost:8000/prestamos \
  -H "Content-Type: application/json" \
  -d '{
    "estudiante_id": 1,
    "libro_id": 1,
    "dias_prestamo": 14
  }'
```

**Respuesta:**
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

### Ejemplo 3: Consultar préstamos vigentes

```bash
curl http://localhost:8000/prestamos/vigentes
```

**Respuesta:**
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

### Ejemplo 4: Registrar devolución

```bash
curl -X POST http://localhost:8000/prestamos/1/devolver
```

**Respuesta:**
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

## Opción 4: Usar Postman

1. Descarga Postman desde https://www.postman.com/downloads/
2. Crea una colección nueva
3. Agrega las siguientes peticiones:

### GET /libros
```
Método: GET
URL: http://localhost:8000/libros
```

### POST /prestamos
```
Método: POST
URL: http://localhost:8000/prestamos
Headers: Content-Type: application/json
Body (JSON):
{
  "estudiante_id": 1,
  "libro_id": 1,
  "dias_prestamo": 14
}
```

### GET /prestamos/vigentes
```
Método: GET
URL: http://localhost:8000/prestamos/vigentes
```

### POST /prestamos/{id}/devolver
```
Método: POST
URL: http://localhost:8000/prestamos/1/devolver
```

## Opción 5: Usar Python (requests)

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# 1. Listar libros
response = requests.get(f"{BASE_URL}/libros")
libros = response.json()
print("Libros disponibles:")
for libro in libros:
    print(f"- {libro['titulo']} ({libro['cantidad_disponible']} disponibles)")

# 2. Crear un préstamo
new_prestamo = {
    "estudiante_id": 1,
    "libro_id": 1,
    "dias_prestamo": 14
}
response = requests.post(f"{BASE_URL}/prestamos", json=new_prestamo)
prestamo = response.json()
prestamo_id = prestamo['id']
print(f"\nPréstamo creado con ID: {prestamo_id}")

# 3. Consultar vigentes
response = requests.get(f"{BASE_URL}/prestamos/vigentes")
vigentes = response.json()
print(f"\nPréstamos vigentes: {len(vigentes)}")

# 4. Registrar devolución
response = requests.post(f"{BASE_URL}/prestamos/{prestamo_id}/devolver")
prestamo_devuelto = response.json()
print(f"\nPréstamo {prestamo_id} devuelto el {prestamo_devuelto['fecha_devolucion']}")
```

## Flujo Completo: Escenario Real

Imagine que Juan Pérez (estudiante_id: 1) quiere:
1. Ver qué libros hay disponibles
2. Pedir prestado "Clean Code"
3. Después de leerlo, devolverlo

### Paso 1: Listar libros
```bash
curl http://localhost:8000/libros | jq '.[] | {titulo, cantidad_disponible}'
```

### Paso 2: Crear préstamo
```bash
PRESTAMO=$(curl -s -X POST http://localhost:8000/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudiante_id": 1, "libro_id": 1, "dias_prestamo": 14}')

PRESTAMO_ID=$(echo $PRESTAMO | jq '.id')
echo "Préstamo creado con ID: $PRESTAMO_ID"
```

### Paso 3: Verificar préstamo activo
```bash
curl http://localhost:8000/prestamos/vigentes | jq '.[] | select(.estudiante_id==1)'
```

### Paso 4: Devolver libro
```bash
curl -X POST http://localhost:8000/prestamos/$PRESTAMO_ID/devolver
```

### Paso 5: Verificar que ya no está en vigentes
```bash
curl http://localhost:8000/prestamos/vigentes | jq '.[] | select(.estudiante_id==1)'
# Resultado vacío si no hay más préstamos vigentes
```

## Testing: Casos de Error

### Error 1: Estudiante no existe
```bash
curl -X POST http://localhost:8000/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudiante_id": 999, "libro_id": 1, "dias_prestamo": 14}'
```

**Respuesta (404):**
```json
{
  "detail": "Estudiante con ID 999 no encontrado"
}
```

### Error 2: No hay ejemplares disponibles
Primero crea 2 préstamos del mismo libro (máximo 3), luego intenta crear uno más:
```bash
# Suponiendo que ya hay 3 libros 1 prestados
curl -X POST http://localhost:8000/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudiante_id": 1, "libro_id": 1, "dias_prestamo": 14}'
```

**Respuesta (400):**
```json
{
  "detail": "No hay ejemplares disponibles del libro 'Clean Code'"
}
```

### Error 3: Devolver dos veces el mismo préstamo
```bash
# Primera devolución
curl -X POST http://localhost:8000/prestamos/1/devolver

# Segunda devolución (error)
curl -X POST http://localhost:8000/prestamos/1/devolver
```

**Respuesta (400):**
```json
{
  "detail": "Este préstamo ya fue devuelto"
}
```

## Tips Útiles

### Instalar herramientas CLI
```bash
# Para parsear JSON desde curl
sudo apt install jq  # Linux/Mac

# O usar Python
curl http://localhost:8000/libros | python -m json.tool
```

### Crear un alias para las peticiones
```bash
alias api_libros='curl -s http://localhost:8000/libros | jq'
alias api_vigentes='curl -s http://localhost:8000/prestamos/vigentes | jq'
```

### Monitorear cambios en tiempo real
```bash
watch -n 2 'curl -s http://localhost:8000/prestamos/vigentes | jq length'
```

## Automatización: Script bash para flujo completo

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"

echo "=== Flujo Completo de Préstamo ==="

# Paso 1: Listar libros
echo -e "\n1. Listando libros..."
LIBROS=$(curl -s "$BASE_URL/libros")
echo $LIBROS | jq '.'

# Paso 2: Crear préstamo
echo -e "\n2. Creando préstamo..."
PRESTAMO=$(curl -s -X POST "$BASE_URL/prestamos" \
  -H "Content-Type: application/json" \
  -d '{"estudiante_id": 1, "libro_id": 2, "dias_prestamo": 7}')
PRESTAMO_ID=$(echo $PRESTAMO | jq '.id')
echo "Préstamo ID: $PRESTAMO_ID"

# Paso 3: Consultar vigentes
echo -e "\n3. Consultando préstamos vigentes..."
curl -s "$BASE_URL/prestamos/vigentes" | jq '.'

# Paso 4: Devolver
echo -e "\n4. Registrando devolución..."
curl -s -X POST "$BASE_URL/prestamos/$PRESTAMO_ID/devolver" | jq '.'

echo -e "\n=== Flujo completado ==="
```

Guarda esto en `test_flow.sh`, hazlo ejecutable con `chmod +x test_flow.sh` y ejecuta con `./test_flow.sh`
