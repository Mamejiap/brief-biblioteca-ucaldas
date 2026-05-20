# Documentación Técnica - API Biblioteca UCaldas v1

## Arquitectura de la Aplicación

La API sigue una arquitectura de **layered architecture** simplificada, ideal para aplicaciones con almacenamiento en memoria:

```
┌─────────────────────────────────────┐
│     Capa de Presentación (API)      │
│  FastAPI Endpoints & Validaciones   │
├─────────────────────────────────────┤
│     Capa de Lógica de Negocio       │
│  BibliotecaRepository (en memoria)  │
├─────────────────────────────────────┤
│      Capa de Datos (Memoria RAM)    │
│  Diccionarios Python (libros,       │
│  estudiantes, préstamos)            │
└─────────────────────────────────────┘
```

## Componentes

### 1. **Modelos (Pydantic)**
Definen la estructura de datos que se envían y reciben:
- `Libro` - Información del libro
- `Estudiante` - Datos del estudiante
- `CrearPrestamo` - Request para crear préstamo
- `Prestamo` - Respuesta de préstamo
- `PrestamosVigentes` - Vista enriquecida de préstamos
- `RegistroDevoluccion` - Request para devolución

### 2. **Repository (Capa de Persistencia)**
La clase `BibliotecaRepository` gestiona:
- Almacenamiento de datos en memoria (diccionarios)
- Lógica de negocio (validaciones, cambios de estado)
- Métodos CRUD para cada entidad

**Método Clave**: `obtener_prestamos_vigentes()`
```python
def obtener_prestamos_vigentes(self) -> List[dict]:
    # Filtra préstamos no devueltos
    # Actualiza estado a VENCIDO si pasó la fecha
    # Retorna lista actualizada
```

### 3. **Endpoints (Rutas)**
Cada endpoint valida:
1. Existencia de recursos (estudiante, libro)
2. Disponibilidad (ejemplares disponibles)
3. Estado (no hacer devoluciones duplicadas)
4. Datos de entrada (días > 0)

### 4. **Estados de Préstamo**
```
┌─────────┐
│ ACTIVO  │ ← Préstamo vigente, dentro del plazo
└────┬────┘
     │ (Si se pasa fecha de vencimiento)
     ▼
┌─────────┐
│ VENCIDO │ ← Préstamo atrasado
└────┬────┘
     │ (Al registrar devolución)
     ▼
┌──────────┐
│ DEVUELTO │ ← Préstamo completado
└──────────┘
```

## Flujo de Operaciones

### Crear Préstamo
```
1. Validar que estudiante existe
2. Validar que libro existe
3. Validar cantidad disponible > 0
4. Validar días_prestamo > 0
5. Crear objeto prestamo con:
   - fecha_prestamo = ahora
   - fecha_vencimiento = ahora + dias_prestamo
   - estado = ACTIVO
6. Decrementar cantidad_disponible del libro
7. Retornar prestamo creado
```

### Consultar Vigentes
```
1. Iterar sobre todos los préstamos
2. Para cada uno con estado != DEVUELTO:
   a. Si fecha_vencimiento < ahora:
      - Actualizar estado a VENCIDO
   b. Enriquecer con datos de estudiante y libro
   c. Calcular dias_restantes = fecha_vencimiento - ahora
3. Retornar lista enriquecida
```

### Registrar Devolución
```
1. Validar que préstamo existe
2. Validar que estado != DEVUELTO
3. Actualizar:
   - fecha_devolucion = ahora
   - estado = DEVUELTO
4. Incrementar cantidad_disponible del libro
5. Retornar préstamo actualizado
```

## Manejo de Errores

### Códigos HTTP utilizados:
- `200 OK` - Operación exitosa (GET)
- `201 Created` - Recurso creado (POST)
- `400 Bad Request` - Error de validación
- `404 Not Found` - Recurso no encontrado

### Estructura de Error:
```json
{
  "detail": "Descripción del error"
}
```

### Ejemplos de Validaciones:
```python
# Estudiante no existe
404: "Estudiante con ID 999 no encontrado"

# Libro no disponible
400: "No hay ejemplares disponibles del libro 'Clean Code'"

# Valores inválidos
400: "El número de días debe ser mayor a 0"

# Estado inválido
400: "Este préstamo ya fue devuelto"
```

## Datos en Memoria

### Ventajas
✓ Rápido y sin configuración
✓ Ideal para pruebas y desarrollo
✓ No requiere base de datos

### Limitaciones
✗ Datos se pierden al reiniciar
✗ No escalable a múltiples instancias
✗ No es adecuado para producción

## Extensibilidad

### Para migrar a Base de Datos (v2):
1. Reemplazar diccionarios con SQLAlchemy ORM
2. Usar migrations (Alembic)
3. Mantener la misma interfaz de endpoints

### Para agregar autenticación:
1. Usar FastAPI Security con JWT
2. Proteger endpoints con `Depends()`
3. Agregar roles (admin, bibliotecario, estudiante)

### Para agregar logging:
1. Configurar `logging` module
2. Registrar operaciones importantes
3. Exportar logs a archivo

### Para agregar caché:
1. Usar Redis o similiar
2. Cachear lista de libros
3. Cachear préstamos vigentes

## Performance

### Complejidad de Operaciones:
- **GET /libros** → O(n) n=número de libros
- **POST /prestamos** → O(1)
- **GET /prestamos/vigentes** → O(n) n=número de préstamos
- **POST /prestamos/{id}/devolver** → O(1)

### Con los datos iniciales (3 libros, 3 estudiantes):
- Todas las operaciones son instantáneas
- Sin latencia de red o I/O

### Consideraciones para escala:
- En versión 2 con BD, usar índices en claves foráneas
- Paginar resultados de listas largas
- Agregar filtros avanzados

## Pruebas

### Flujo de Prueba Completo:
```bash
# 1. Iniciar API
python main.py

# 2. En otra terminal, listar libros
curl http://localhost:8000/libros

# 3. Crear préstamo
curl -X POST http://localhost:8000/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudiante_id": 1, "libro_id": 1, "dias_prestamo": 14}'

# 4. Consultar vigentes
curl http://localhost:8000/prestamos/vigentes

# 5. Devolver libro
curl -X POST http://localhost:8000/prestamos/1/devolver

# 6. Verificar que está devuelto
curl http://localhost:8000/prestamos/vigentes
```

## Casos de Uso Cubiertos

| Caso de Uso | Endpoint | Método | Status |
|---|---|---|---|
| Listar libros | `/libros` | GET | ✅ |
| Crear préstamo | `/prestamos` | POST | ✅ |
| Consultar vigentes | `/prestamos/vigentes` | GET | ✅ |
| Registrar devolución | `/prestamos/{id}/devolver` | POST | ✅ |
| Verificar salud API | `/health` | GET | ✅ |
| Información API | `/` | GET | ✅ |

## Referencias FastAPI

- [Documentación oficial](https://fastapi.tiangolo.com/)
- [Pydantic Models](https://docs.pydantic.dev/)
- [HTTP Status Codes](https://developer.mozilla.org/es/docs/Web/HTTP/Status)
- [Uvicorn Server](https://www.uvicorn.org/)
