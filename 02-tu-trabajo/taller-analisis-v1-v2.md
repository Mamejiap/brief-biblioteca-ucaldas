# Bitácora del Taller — Análisis V1 vs V2

---

## Contexto

Durante este taller trabajarás con dos versiones de la misma API REST para gestión de préstamos de una biblioteca universitaria.

- **`version_1`** — Implementación simple en Python con FastAPI. Sin validaciones formales, sin arquitectura en capas, sin tests.
- **`version_2`** — Implementación en Python con Clean Architecture, validaciones con Pydantic, manejo de errores tipado y suite completa de tests unitarios e integración.

El objetivo no es determinar cuál versión es "mejor", sino comprender qué impacto tiene la estructura del código sobre la capacidad de probarlo.

---

## Antes de empezar

Levanta ambos servidores en terminales separadas:

```bash
# Terminal 1
cd version_1
py main.py
```

```bash
# Terminal 2
cd version_2
uvicorn app.main:app --reload
```

Verifica que ambos respondan:

```bash
curl http://localhost:8000/
curl http://localhost:8001/
```

También puedes revisar la documentación automática en el navegador:

```
V1: http://localhost:8000/docs
V2: http://localhost:8001/docs
```

---

## Bloque 1 — Lectura y comparación estructural

### Ejercicio 1.1 — Inventario de diferencias

| Dimensión | v1 | v2 |
|---|---|---|
| Lenguaje | Python | Python |
| Validación de entradas al servidor | `pydantic` básico para tipar el body de entrada | Pydantic con schemas de entrada/salida separados + validación de reglas de negocio en la capa de servicio |
| Manejo de errores HTTP | `404 Not Found` cuando un libro o préstamo no existe; `400 Bad Request` por ISBN duplicado, libro no disponible, fecha inválida o préstamo ya completado; `201 Created` en creación de libros y préstamos | Jerarquía custom (`EntidadNoEncontrada`, `ConflictoDeNegocio`) mapeada a status codes específicos. Respuesta con `error` (código máquina) y `mensaje` (texto legible) |
| Arquitectura (número de capas) | Básica — principalmente en `main.py` | 4 capas: `routers/` (HTTP) → `services/` (reglas de negocio) → `repositories/` (acceso a datos) → `db/` (almacenamiento) |
| Tests incluidos |No incluye tests automatizados, solo propone pruebas manuales con curl, Swagger UI, REST Client o Postman. | 13+ tests con pytest cubriendo RN1–RN8 |
| Tipado de datos | `pydantic` models importados desde `models`; `typing` estándar de Python (listas, diccionarios) | Modelos de dominio Pydantic con tipos estrictos (`Literal`), schemas de API separados de los modelos de dominio |
| Forma de iniciar la aplicación | `py main.py` | `uvicorn app.main:app --reload` desde `biblioteca-api/` |

---

### Ejercicio 1.2 — Rastreo de RN1 (límite de préstamos simultáneos por tipo de estudiante)

**1. ¿En qué archivo está en v1? ¿En cuántas líneas se implementa?**

En `main.py`, dentro de la función `crear_prestamo`, la validación se implementa aproximadamente en 5 líneas: primero revisa si el libro no está disponible y luego lanza una excepción HTTP con el código de error y el mensaje correspondiente.

**2. ¿En qué archivo(s) está en v2? ¿Qué capas atraviesa?**

- **Constante de configuración:** `biblioteca-api/app/services/prestamo_service.py` línea 16
  ```python
  _LIMITE_PRESTAMOS = {"pregrado": 3, "postgrado": 5}
  ```
- **Lógica de verificación:** `prestamo_service.py` líneas 70–76
  ```python
  activos = self.prestamo_repo.get_activos_by_estudiante(estudiante_codigo)
  limite = _LIMITE_PRESTAMOS[estudiante.nivel_academico]
  if len(activos) >= limite:
      raise ConflictoDeNegocio(...)
  ```
- **Consulta de préstamos activos:** `biblioteca-api/app/repositories/prestamo_repo.py` → `get_activos_by_estudiante()`

Atraviesa **3 capas:** `routers/prestamos.py` (recibe el request) → `services/prestamo_service.py` (aplica la regla) → `repositories/prestamo_repo.py` (consulta la base de datos).

**3. Si el cliente pide cambiar el límite de pregrado de 3 a 4, ¿cuántos archivos hay que modificar en cada versión?**

| | Archivos a modificar |
|---|---|
| **v1** | Principalmente **1 archivo**: `main.py`. Como la regla está escrita directamente dentro del endpoint, el cambio se haría en la función `crear_prestamo`, pero ya que no valida el número maximo, se debe implmentar practicamente desde cero |
| **v2** | **1 archivo, 1 línea:** cambiar `"pregrado": 3` a `"pregrado": 4` en la constante `_LIMITE_PRESTAMOS` de `prestamo_service.py:16` |

**4. ¿Cómo sabrías que el cambio no rompió nada en cada versión?**

- **v1:** No hay forma automatizada. Habría que probar manualmente con `curl` varios escenarios. Alta probabilidad de dejar casos sin cubrir.
- **v2:** Ejecutar `pytest tests/test_prestamos.py`. Los tests `test_rn1_limite_pregrado_max_3` y `test_rn1_limite_postgrado_max_5` verifican los límites automáticamente. Si se cambia el límite, el test `test_rn1_limite_pregrado_max_3` fallaría y alertaría que el comportamiento cambió, permitiendo actualizar el test para reflejar el nuevo límite o identificar una regresión.

---

## Bloque 2 — Análisis de calidad y comportamiento ante errores

**Modalidad:** Parejas  
**Tiempo:** 30 minutos

### Ejercicio 2.1 — El request que no debería funcionar

**Request ejecutado:**

```bash
# Contra v1 (puerto 8000):
curl.exe -i -X POST http://localhost:8000/prestamos -H "Content-Type: application/json" -d "{\"estudianteId\":\"NO-EXISTE\",\"ejemplarId\":\"abc\"}"

# Contra v2 (puerto 8001):
curl -s -X POST http://localhost:8001/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudiante_codigo": "NO-EXISTE", "ejemplar_id": "abc"}'
```

**Respuestas observadas:**

| Pregunta | v1 | v2 |
|---|---|---|
| Código HTTP | `201 Created` — crea el préstamo aun con datos inválidos | `404 Not Found` |
| Cuerpo de la respuesta | `{"id": 2, "id_libro": 2, "id_usuario": "NO EXISTE", "fecha_prestamo": "2026-05-19T14:44:58.232664", "fecha_devolución_esperada": "...", "fecha_devolución_real": null, "estado": "vigente"}` | `{"error": "estudiante_no_encontrado", "mensaje": "Estudiante 'NO-EXISTE' no encontrado."}` |
| ¿Qué respuesta es más útil? | Menos útil — no valida si el usuario existe y genera datos inconsistentes de forma silenciosa | Más útil — el campo `error` permite que el cliente maneje casos específicos; el mensaje es claro y accionable |
| Si `ejemplarId` llega como string en lugar de número | `{"detail": "El libro con ID 2 no está disponible"}` — interpreta o ignora el tipo y busca en la DB | v2 Pydantic valida el tipo antes de llegar al servicio; retorna `422 Unprocessable Entity` con el campo y tipo esperado |

**Análisis:**
- v1 no valida la existencia del usuario antes de crear el préstamo: un `id_usuario: "NO EXISTE"` genera un préstamo real en el sistema con datos basura, sin ningún error visible.
- v2 separa errores de **validación de formato** (422 automático de Pydantic) de errores de **dominio/negocio** (404 `EntidadNoEncontrada`, 409 `ConflictoDeNegocio`).

---

### Ejercicio 2.2 — Comparar errores de dominio (ejemplar ya prestado)

**Pasos para reproducir:**

```bash
# Paso 1 — crear primer préstamo con ejemplar EJ-001
curl -X POST http://localhost:8001/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudiante_codigo": "EST-001", "ejemplar_id": "EJ-001"}'

# Paso 2 — intentar prestar el mismo ejemplar a otro estudiante
curl -s -X POST http://localhost:8001/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudiante_codigo": "EST-002", "ejemplar_id": "EJ-001"}'
```

| Aspecto | v1 | v2 |
|---|---|---|
| Código HTTP | `400 Bad Request` | `409 Conflict` |
| Campo `error` en la respuesta | No tiene campo `error` — usa el campo `detail` | `"ejemplar_no_disponible"` |
| Mensaje legible | `{"detail": "El libro con ID 1 no está disponible"}` | `"El ejemplar no está disponible para préstamo."` |
| Información adicional (detalles) | No entrega detalles adicionales, solo el mensaje en `detail` | Ninguna adicional, pero el código de error es suficiente para que el cliente actúe |
| ¿Expone información interna del servidor? | No — solo muestra mensaje controlado | No |

**Observación clave:** v2 usa `409 Conflict` (semánticamente correcto para conflicto de estado de recurso) mientras v1 usa `400 Bad Request` (que implica datos de entrada incorrectos, no un conflicto de negocio). Esta distinción es importante para que los clientes distingan entre "enviaste datos inválidos" y "la operación no se puede hacer ahora por el estado del sistema".

---

## Bloque 3 — Análisis de los tests de v2

### Ejercicio 3.1 — Lectura del test de CrearPrestamo

> **Nota:** El taller referencia `tests/unit/CrearPrestamo.test.ts` (TypeScript). El equivalente Python es `biblioteca-api/tests/test_prestamos.py`.

**1. ¿Qué técnica de aislamiento se usa?**

Los tests de v2 usan **fixtures de pytest** con reset completo de la base de datos en memoria antes de cada test (`autouse=True` en `reset_db`). No es un mock de repositorios en sentido estricto — es un **fake** (base de datos en memoria que se vacía). Esto los clasifica como tests de **integración liviana**: prueban el comportamiento completo incluyendo la capa HTTP, pero sin base de datos real ni red externa.

**2. ¿Se levanta algún servidor HTTP para ejecutar este test? ¿Por qué importa esto?**

Sí: `TestClient(app)` de FastAPI levanta la aplicación completa internamente. **No** abre un puerto de red real (lo que sería más lento), pero sí pasa los requests por el stack HTTP completo (routing, middleware, serialización). Esto importa porque:
- Es más lento que un test unitario puro con mocks (que prueba solo el servicio)
- Pero valida que el endpoint, el schema de respuesta y el servicio funcionen integrados

**3. ¿En qué líneas se prueba RN4 (multa pendiente) y RN3 (préstamos vencidos)?**

Nota: el enunciado del taller invierte los números. Según la implementación real:
- **RN3 — multa pendiente:** función `test_rn3_bloqueo_multa_pendiente` (bloquea préstamo si hay multa sin pagar)
- **RN2 — préstamo vencido pendiente:** función `test_rn2_bloqueo_prestamo_vencido` (bloquea si hay préstamo vencido sin devolver)

Ambas verifican que el service lanza `ConflictoDeNegocio` con el código de error correcto y que el endpoint devuelve `409`.

**4. ¿Cuánto tiempo tarda en ejecutarse?**

La suite completa de préstamos (~15 tests) tarda aproximadamente **< 1 segundo** gracias a que todo opera en memoria. Esto ilustra la ventaja principal de diseñar para testabilidad: ciclo de feedback instantáneo.

---

## Bloque 4 — Escritura de tests

### Ejercicio 4.1 — Test unitario: posgrado falla al intentar el sexto préstamo

**Archivos creados:**
- `biblioteca-api/tests/unit/__init__.py` (vacío — necesario para que pytest descubra el subdirectorio)
- `biblioteca-api/tests/unit/test_rn1_posgrado_unitario.py` (test unitario puro)

**Adaptación al stack real:** El enunciado usa "posgrado" (referencia TypeScript/Express). El modelo Python real (`app/models/estudiante.py`) define el campo como `Literal["pregrado", "postgrado"]`. Se usa `"postgrado"` en el test.

---

**Código del test** (`biblioteca-api/tests/unit/test_rn1_posgrado_unitario.py`):

```python
"""
Test unitario puro — RN1: límite de préstamos simultáneos para estudiantes de postgrado.

Estrategia de aislamiento:
    Se instancia PrestamoService directamente (sin TestClient ni HTTP).
    Los 6 repositorios se reemplazan con unittest.mock.MagicMock.
    No se toca la base de datos en memoria (memoria.py) en ningún momento.
    Resultado: cada test corre en < 10 ms y no depende de estado global.
"""
import os
os.environ["TESTING"] = "true"

from datetime import date, timedelta
from unittest.mock import MagicMock
import pytest

from app.core.exceptions import ConflictoDeNegocio
from app.models.ejemplar import Ejemplar
from app.models.estudiante import Estudiante
from app.models.libro import Libro
from app.models.prestamo import Prestamo
from app.services.prestamo_service import PrestamoService


def _prestamos_activos(n: int) -> list:
    """Devuelve n Prestamos con fechas futuras (RN2 no se dispara)."""
    hoy = date.today()
    return [
        Prestamo(
            id=f"P-MOCK-{i:02d}",
            estudiante_cod="EST-PG",
            ejemplar_id=f"EJ-MOCK-{i:02d}",
            fecha_prestamo=hoy - timedelta(days=i),
            fecha_devolucion_esperada=hoy + timedelta(days=10),
            estado="activo",
        )
        for i in range(1, n + 1)
    ]


def _build_service(activos_existentes: list) -> PrestamoService:
    """Construye PrestamoService con todos sus colaboradores mockeados."""
    estudiante = Estudiante(
        codigo="EST-PG",
        nombre="Laura Gómez",
        programa_academico="Maestría en Sistemas",
        nivel_academico="postgrado",
    )
    ejemplar = Ejemplar(id="EJ-NEW", cod_libro="LIB-001", estado="disponible")
    libro = Libro(
        codigo="LIB-001", titulo="Estructuras de Datos Avanzadas",
        autor="Autor Test", sala="Sala B", alta_demanda=False,
    )

    prestamo_repo   = MagicMock()
    estudiante_repo = MagicMock()
    ejemplar_repo   = MagicMock()
    libro_repo      = MagicMock()
    reserva_repo    = MagicMock()
    multa_service   = MagicMock()

    estudiante_repo.get_by_codigo.return_value = estudiante
    ejemplar_repo.get_by_id.return_value       = ejemplar
    libro_repo.get_by_codigo.return_value      = libro
    prestamo_repo.get_activos_by_estudiante.return_value = activos_existentes
    multa_service.multa_repo.get_pendientes_by_estudiante.return_value = []
    prestamo_repo.save.side_effect = lambda p: p

    return PrestamoService(
        prestamo_repo=prestamo_repo,
        estudiante_repo=estudiante_repo,
        ejemplar_repo=ejemplar_repo,
        libro_repo=libro_repo,
        multa_service=multa_service,
        reserva_repo=reserva_repo,
    )


class TestRN1PostgradoLimitePrestamos:

    def test_quinto_prestamo_se_permite(self):
        """Happy path: con 4 activos el quinto se otorga sin error."""
        service = _build_service(activos_existentes=_prestamos_activos(4))
        resultado = service.crear_prestamo("EST-PG", "EJ-NEW", date.today())

        assert resultado is not None
        assert resultado.estado == "activo"
        assert resultado.estudiante_cod == "EST-PG"
        service.prestamo_repo.save.assert_called_once()

    def test_sexto_prestamo_lanza_conflicto_de_negocio(self):
        """RN1: con 5 activos el sexto lanza ConflictoDeNegocio."""
        service = _build_service(activos_existentes=_prestamos_activos(5))

        with pytest.raises(ConflictoDeNegocio) as exc_info:
            service.crear_prestamo("EST-PG", "EJ-NEW", date.today())

        assert exc_info.value.codigo_error == "limite_prestamos_alcanzado"
        assert "5" in exc_info.value.mensaje
        service.prestamo_repo.save.assert_not_called()
```

---

**Traza lógica del test (verificación manual de correctitud):**

| Paso en `crear_prestamo` | Mock configurado | Resultado esperado |
|---|---|---|
| `estudiante_repo.get_by_codigo("EST-PG")` | Retorna `Estudiante(nivel_academico="postgrado")` | `limite = _LIMITE_PRESTAMOS["postgrado"]` → `5` |
| `ejemplar_repo.get_by_id("EJ-NEW")` | Retorna `Ejemplar(estado="disponible")` | Sigue adelante |
| `libro_repo.get_by_codigo("LIB-001")` | Retorna `Libro(alta_demanda=False)` | Sigue adelante |
| **RN1** `get_activos_by_estudiante` | Retorna lista de **5** objetos | `len(activos) >= 5` → `True` → lanza `ConflictoDeNegocio("limite_prestamos_alcanzado")` ✓ |
| **RN1 happy path** | Retorna lista de **4** objetos | `len(activos) >= 5` → `False` → continúa |
| **RN2** (vencidos) | 4 prestamos con `fecha_devolucion_esperada = hoy + 10d` | `fecha < hoy` → `False` para todos → pasa ✓ |
| **RN3** (multas) | `get_pendientes_by_estudiante` → `[]` | Lista vacía → pasa ✓ |
| **RN4** (disponible) | `ejemplar.estado == "disponible"` | `True` → pasa ✓ |
| `prestamo_repo.save(prestamo)` | `side_effect = lambda p: p` | Retorna el Prestamo creado ✓ |

---

**Comando para ejecutar localmente:**

```bash
cd biblioteca-api
pytest tests/ -v --tb=short
```

**Resultado esperado (salida de pytest):**

```
tests/unit/test_rn1_posgrado_unitario.py::TestRN1PostgradoLimitePrestamos::test_quinto_prestamo_se_permite PASSED
tests/unit/test_rn1_posgrado_unitario.py::TestRN1PostgradoLimitePrestamos::test_sexto_prestamo_lanza_conflicto_de_negocio PASSED
```

---

## Reflexiones finales

### ¿Qué es lo más importante que muestra esta comparación?

La diferencia de testabilidad **no es accidental**: es consecuencia directa de la arquitectura. Cuando la lógica de negocio vive mezclada con el framework HTTP, es imposible probarla sin levantar el framework. La separación en capas (Clean Architecture) no es complejidad gratuita — es lo que permite verificar cada regla de negocio de forma rápida e independiente.

### Una observación concreta

v2 tiene `_LIMITE_PRESTAMOS = {"pregrado": 3, "postgrado": 5}` en una constante. Cambiar ese valor es inmediato y los tests te dicen si algo rompió. En v1, esa regla no existe ni como código — si el cliente la pide, hay que inventarla desde cero, sin red de seguridad.
