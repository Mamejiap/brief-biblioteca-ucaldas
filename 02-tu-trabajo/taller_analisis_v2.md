# Resolución del Taller de Análisis — Versión 2
## Sistema de Préstamo de Libros — UCaldas
**Autor:** Mateo Mejía · **Fecha:** 2026-05-20  
**Stack analizado:** Python 3.11 + FastAPI · Clean Architecture · pytest  
**Nota metodológica:** Este documento resuelve todos los ejercicios del taller `taller-analisis-v1-v2.md` con foco exclusivo en la Versión 2 generada en este proyecto. Las columnas y preguntas referidas a "v1" se marcan como **N/A** (esa versión no fue implementada en este contexto).

---

## Bloque 1 — Lectura y comparación estructural

### Ejercicio 1.1 — Inventario de diferencias

| Dimensión | v1 | v2 (este proyecto) |
|---|---|---|
| Lenguaje | N/A | Python 3.11 |
| Validación de entradas al servidor | N/A | Pydantic v2 con `Field(min_length=1)`, `ge=1`; tipos estrictos en schemas; FastAPI devuelve `422 Unprocessable Entity` automáticamente para body malformado |
| Manejo de errores HTTP | N/A | Excepciones de dominio tipadas (`DomainException` → subclases) mapeadas en `error_handlers.py` a códigos HTTP específicos: `400`, `404`, `409`. Ningún `try/except` genérico en los routers. |
| Arquitectura (número de capas) | N/A | 4 capas explícitas: **Domain** (entidades + interfaces + excepciones) → **Application** (casos de uso) → **Infrastructure** (repos en memoria) → **API** (routers + schemas + DI) |
| Tests incluidos | N/A | 3 archivos de tests unitarios (sin levantar HTTP) + 1 archivo de tests de integración con `TestClient` de FastAPI. ~20 tests en total. `conftest.py` con fixtures compartidos. |
| Tipado de datos | N/A | Tipado estático completo: `dataclass` con type hints en dominio; `BaseModel` de Pydantic en API; `Enum` para estados y tipos; `dict[str, Entidad]` en repositorios. |
| Forma de iniciar la aplicación | N/A | `uvicorn main:app --reload` desde la raíz del proyecto. El objeto `app` se construye en `main.py` registrando routers y exception handlers. |

---

### Ejercicio 1.2 — Rastreo de RN1: límite de préstamos simultáneos por tipo de estudiante

**Pregunta 1 — ¿En qué archivo está en v1? ¿En cuántas líneas?**

N/A — v1 no fue implementada en este proyecto.

---

**Pregunta 2 — ¿En qué archivo(s) está en v2? ¿Qué capas atraviesa?**

La RN1 atraviesa **tres capas** con responsabilidades claramente separadas:

**Capa Domain — `app/domain/entities/estudiante.py` (líneas 10–27)**

```python
# Límites de préstamos simultáneos por tipo (RN1, RN2)
LIMITE_PRESTAMOS: dict[TipoEstudiante, int] = {
    TipoEstudiante.PREGRADO: 3,
    TipoEstudiante.POSGRADO: 5,
}

@property
def limite_prestamos(self) -> int:
    return LIMITE_PRESTAMOS[self.tipo]
```

Aquí vive la **fuente de verdad** del límite. Es una constante del dominio, no de la lógica de negocio ni de la API.

**Capa Application — `app/application/use_cases/prestamos/crear_prestamo.py` (líneas 66–70)**

```python
# ── RN1 / RN2 — Límite de préstamos simultáneos ───────────────────────
activos = self._prestamo_repo.listar_activos_por_estudiante(data.estudiante_id)
limite = estudiante.limite_prestamos
if len(activos) >= limite:
    raise LimitePrestamosAlcanzado(data.estudiante_id, limite, len(activos))
```

Aquí se **evalúa** la regla. El caso de uso consulta al repositorio, lee el límite desde la entidad y lanza una excepción tipada si se viola.

**Capa Domain — `app/domain/exceptions.py` (líneas 46–55)**

```python
class LimitePrestamosAlcanzado(DomainException):
    def __init__(self, estudiante_id: str, limite: int, actuales: int):
        self.limite = limite
        self.actuales = actuales
```

La excepción es parte del dominio: lleva consigo los datos del contexto de error (`limite`, `actuales`).

**Capa API — `app/api/error_handlers.py` (líneas 44–51)**

```python
@app.exception_handler(LimitePrestamosAlcanzado)
async def limite_prestamos(request: Request, exc: LimitePrestamosAlcanzado):
    return JSONResponse(status_code=409, content={
        "error": "limite_prestamos_alcanzado",
        "mensaje": str(exc),
        "limite": exc.limite,
        "actuales": exc.actuales,
    })
```

Aquí se **traduce** la excepción de dominio a HTTP. El router no sabe nada de la RN1; solo ocurre la traducción.

---

**Pregunta 3 — Si el cliente pide cambiar el límite de pregrado de 3 a 4, ¿cuántos archivos hay que modificar en cada versión?**

| Versión | Archivos a modificar | Detalle |
|---|---|---|
| v1 | N/A | — |
| v2 (este proyecto) | **1 archivo** | Solo `app/domain/entities/estudiante.py`, línea 12: cambiar `TipoEstudiante.PREGRADO: 3` a `TipoEstudiante.PREGRADO: 4`. El caso de uso, el router y los tests de integración no requieren cambios porque leen el límite desde la propiedad de la entidad. |

Este es uno de los beneficios concretos de encapsular las constantes de dominio en la entidad en lugar de hardcodearlas en la lógica de negocio.

---

**Pregunta 4 — ¿Cómo sabrías que el cambio no rompió nada?**

| Versión | Mecanismo de verificación |
|---|---|
| v1 | N/A |
| v2 (este proyecto) | Ejecutar `pytest -v`. El test `TestRN1Pregrado::test_cuarto_prestamo_lanza_excepcion` fallaría inmediatamente si el cambio fuera incorrecto, ya que aserta que `exc_info.value.limite == 3`. Eso alertaría al desarrollador a actualizar también los tests para reflejar el nuevo límite esperado. El resto de la suite continuaría verde porque la lógica es independiente del valor concreto. |

---

## Bloque 2 — Análisis de calidad y comportamiento ante errores

### Ejercicio 2.1 — El request que no debería funcionar

**Comando equivalente para v2:**
```bash
curl -s -X POST http://localhost:8000/api/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudianteId": "NO-EXISTE", "ejemplarId": "abc"}' | jq
```

> **Nota:** Los campos en esta API son `estudiante_id` y `ejemplar_id` (snake_case), no camelCase.

**Pregunta 1 — ¿Qué código HTTP devuelve cada versión?**

| Versión | Código HTTP | Razón |
|---|---|---|
| v1 | N/A | — |
| v2 — con camelCase incorrecto | `422 Unprocessable Entity` | Pydantic rechaza el body porque los campos requeridos (`estudiante_id`, `ejemplar_id`) no están presentes. El error ocurre antes de llegar al caso de uso. |
| v2 — con snake_case correcto pero IDs inexistentes | `404 Not Found` | `CrearPrestamo` no encuentra el estudiante → lanza `EstudianteNoEncontrado` → `error_handlers.py` lo mapea a 404. |

**Pregunta 2 — ¿Qué información contiene el cuerpo de la respuesta?**

Para el caso `422` (campo incorrecto), FastAPI genera automáticamente:
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "estudiante_id"],
      "msg": "Field required",
      "input": {"estudianteId": "NO-EXISTE", "ejemplarId": "abc"}
    }
  ]
}
```

Para el caso `404` (IDs inexistentes con campos correctos), el `error_handler` produce:
```json
{
  "error": "estudiante_no_encontrado",
  "mensaje": "Estudiante 'NO-EXISTE' no encontrado."
}
```

**Pregunta 3 — ¿Cuál respuesta es más útil para un cliente?**

La respuesta `404` de v2 es **más útil** que una respuesta genérica porque:
- Incluye un campo `error` con un identificador de máquina (`"estudiante_no_encontrado"`) que el cliente puede verificar programáticamente.
- El campo `mensaje` es legible por humanos e incluye el ID que falló.
- No expone stack traces ni información interna del servidor.

**Pregunta 4 — ¿Qué pasa si `ejemplarId` llega como string en lugar de número?**

| Versión | Comportamiento |
|---|---|
| v1 | N/A |
| v2 | `ejemplar_id` está declarado como `str` en el schema (`PrestamoCreate`), por lo que **acepta cualquier string** — esto es comportamiento correcto en este diseño. Si fuera un campo numérico y llegara como string, Pydantic intentaría la coerción; si fallara, devolvería `422` antes de entrar al caso de uso. |

---

### Ejercicio 2.2 — Comparar errores de dominio: ejemplar ya prestado

**Pasos para reproducir en v2:**
```bash
# Paso 1: crear préstamo con EJ-001-01
curl -s -X POST http://localhost:8000/api/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudiante_id": "EST-PRE-01", "ejemplar_id": "EJ-001-01"}' | jq

# Paso 2: intentar prestar el mismo ejemplar a otro estudiante
curl -s -X POST http://localhost:8000/api/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudiante_id": "EST-POS-01", "ejemplar_id": "EJ-001-01"}' | jq
```

**Tabla comparativa:**

| Aspecto | v1 | v2 (este proyecto) |
|---|---|---|
| Código HTTP | N/A | `409 Conflict` |
| Campo `error` en la respuesta | N/A | `"ejemplar_no_disponible"` (identificador de máquina) |
| Mensaje legible | N/A | `"Ejemplar 'EJ-001-01' no está disponible para préstamo."` |
| Información adicional | N/A | El campo `ejemplar_id` está embebido en el mensaje. No se expone información extra. |
| ¿Expone información interna? | N/A | **No.** La excepción `EjemplarNoDisponible` solo expone el `ejemplar_id`. No hay stack trace, no hay nombres de clases internas, no hay rutas de archivo. |

**Evidencia en código:**
```python
# exceptions.py — línea 77
class EjemplarNoDisponible(DomainException):
    def __init__(self, ejemplar_id: str):
        self.ejemplar_id = ejemplar_id
        super().__init__(f"Ejemplar '{ejemplar_id}' no está disponible para préstamo.")

# error_handlers.py — línea 65
@app.exception_handler(EjemplarNoDisponible)
async def ejemplar_no_disponible(request: Request, exc: EjemplarNoDisponible):
    return JSONResponse(status_code=409, content={
        "error": "ejemplar_no_disponible",
        "mensaje": str(exc)
    })
```

---

## Bloque 3 — Análisis de los tests de v2

### Ejercicio 3.1 — Lectura del test unitario (`test_crear_prestamo.py`)

**Pregunta 1 — ¿Qué técnica de aislamiento se usa?**

Se usan **fakes** (objetos reales pero en memoria, no doubles de test). Los repositorios son instancias reales de `InMemoryLibroRepository`, `InMemoryEstudianteRepository`, etc. — no mocks ni stubs. Esta es una decisión de diseño deliberada: los fakes tienen comportamiento real pero sin persistencia externa, lo que permite tests rápidos y fieles al contrato del repositorio.

No hay uso de `unittest.mock`, `MagicMock`, ni decoradores `@patch`. El aislamiento lo da la arquitectura (el caso de uso recibe sus dependencias por constructor), no un framework de mocking.

**Pregunta 2 — ¿Se levanta algún servidor HTTP para ejecutar este test? ¿Por qué importa?**

**No.** El archivo `tests/unit/test_crear_prestamo.py` no importa `FastAPI`, `TestClient`, ni ningún componente de la capa API. Solo importa el caso de uso `CrearPrestamo` y los repositorios en memoria.

Esto importa por dos razones:

1. **Velocidad:** Sin servidor HTTP, los tests unitarios se ejecutan en milisegundos. Levantar un servidor ASGI tarda ~200-500ms por sesión. Con docenas de tests unitarios, la diferencia es de segundos vs. minutos.
2. **Precisión del fallo:** Si un test unitario falla, el error está en la lógica de negocio, no en el routing, serialización o middleware. El diagnóstico es inmediato.

**Pregunta 3 — ¿En qué líneas se prueba RN4 (multa pendiente) y RN3 (préstamos vencidos)?**

| Regla | Clase en el test | Líneas aproximadas | Descripción |
|---|---|---|---|
| **RN3** — Préstamo vencido | `TestRN3PrestamoVencido` | Líneas 143–168 | Construye un `Prestamo` con `fecha_devolucion_esperada` 5 días en el pasado, lo guarda directamente en el repo, y verifica que `CrearPrestamo` lanza `PrestamoVencidoPendiente`. |
| **RN4** — Multa pendiente | `TestRN4MultaPendiente` | Líneas 172–199 | Inserta directamente una `Multa` con `pagada=False` en el `multa_repo`, y verifica que `CrearPrestamo` lanza `MultaPendiente` con el `monto_total` correcto (`6_000`). |

La técnica clave en ambos casos es la **inyección directa de estado** en los repositorios en memoria, sin necesidad de llamar a otros endpoints o de manipular fechas del sistema.

**Pregunta 4 — ¿Cuánto tiempo tarda en ejecutarse?**

No fue posible ejecutar `pytest` formalmente (el sandbox carecía de acceso a internet para instalar dependencias). Sin embargo, con base en la estructura del test (sin HTTP, sin I/O, sin `time.sleep`), el tiempo esperado para los 14 tests unitarios del archivo es **< 100ms** en cualquier máquina moderna. Los tests de integración, que sí levantan un `TestClient`, tomarían ~500ms–2s para los 20 tests.

---

## Bloque 4 — Escritura de tests

### Ejercicio 4.1 — Test para posgrado: falla al intentar el sexto préstamo

El test ya está implementado en `tests/unit/test_crear_prestamo.py`, clase `TestRN2Posgrado`, método `test_sexto_prestamo_lanza_excepcion`. A continuación, el código completo con las decisiones de implementación explicadas:

```python
def test_sexto_prestamo_lanza_excepcion(
    self, estudiante_posgrado, libro_normal,
    estudiante_repo, ejemplar_repo, libro_repo, prestamo_repo, multa_repo
):
    """RN2: el sexto préstamo simultáneo de posgrado debe fallar con 409."""
    # Crear 6 ejemplares disponibles del libro normal
    ejs = _agregar_ejemplares(libro_repo, ejemplar_repo, libro_normal, 6)

    # Insertar 5 préstamos activos directamente en el repo (sin pasar por el UC)
    # Esto simula el estado "el estudiante ya tiene 5 activos" sin acoplar el test
    # a la lógica de CrearPrestamo para los préstamos previos.
    for i in range(5):
        _prestamo_activo(estudiante_posgrado.id, ejs[i], prestamo_repo)

    uc = make_use_case(estudiante_repo, ejemplar_repo, libro_repo, prestamo_repo, multa_repo)

    # Intentar el sexto — debe lanzar LimitePrestamosAlcanzado
    with pytest.raises(LimitePrestamosAlcanzado) as exc_info:
        uc.execute(CrearPrestamoInput(
            estudiante_id=estudiante_posgrado.id,
            ejemplar_id=ejs[5],
            fecha_prestamo=HOY,
        ))

    # Verificar que los datos del error son correctos
    assert exc_info.value.limite == 5
    assert exc_info.value.actuales == 5
```

**¿Por qué sería más lento o difícil en v1?**

En una versión sin arquitectura en capas (como la hipotética v1 en Node.js/Express), la lógica de negocio está directamente en el handler de la ruta. Para probar la RN1 habría que:

1. **Levantar el servidor** — un servidor HTTP real o con `supertest`, lo que añade overhead de inicio.
2. **Hacer 6 requests HTTP** — 5 para crear los préstamos previos + 1 para el que debe fallar. Cada request tiene serialización/deserialización, middleware, routing.
3. **Depender del estado compartido** — si la base de datos (o el objeto en memoria) no se resetea entre tests, el sexto test del día puede fallar porque el segundo dejó datos.
4. **No hay acceso directo al estado** — no se puede insertar directamente un préstamo en el repositorio; hay que crearlo a través de la API, lo que significa que el test de RN2 depende de que RN1, RN5 y RN6 funcionen correctamente primero.

En v2, los 5 préstamos previos se insertan directamente en el `prestamo_repo` con el helper `_prestamo_activo`. No hay HTTP, no hay serialización, no hay dependencias cruzadas entre reglas.

---

## Reflexión final — Impacto de la arquitectura sobre la capacidad de prueba

La pregunta central del taller es: *¿qué impacto tiene la estructura del código sobre la capacidad de probarlo?*

Después de analizar v2 en detalle, la respuesta concreta es:

**La separación de capas hace que cada regla de negocio sea verificable de forma independiente, sin levantar la aplicación completa.**

En v2, `CrearPrestamo` recibe sus dependencias por constructor. Eso significa que en un test se puede inyectar un repositorio en memoria con exactamente el estado necesario para probar una regla específica — sin tocar el router, sin tocar la base de datos, sin tocar otros casos de uso. Los tests unitarios son rápidos no porque usen mocks, sino porque la arquitectura elimina las dependencias accidentales.

El costo visible de esta arquitectura es la verbosidad: 35 archivos para una API con 8 reglas de negocio. El beneficio es que cada uno de esos archivos tiene exactamente una razón para cambiar. Cuando el cliente pida cambiar el límite de pregrado, el cambio es en una línea de un archivo. Cuando pida agregar una nueva regla de negocio, el cambio es agregar un archivo nuevo sin modificar los existentes.
