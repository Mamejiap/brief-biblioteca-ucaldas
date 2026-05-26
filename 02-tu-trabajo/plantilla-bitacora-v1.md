# Bitácora del Taller — Danna Alexandra Madrid
# Proyecto: Sistema de Préstamo de Libros — Versión 1 (Python / FastAPI)


---

## Sección 1 — Hallazgos de la auditoría humana (Etapa 3)

### Inventario inicial

- **Archivos generados por la IA:** 10 archivos en total.
  - Archivos base: `.env.example`, `.gitignore`, `ARQUITECTURA.md`, `EJEMPLOS.md`, `main.py`, `README.md`, `requests.http`, `requirements.txt`, `run.bat`, `run.sh`

- **Dependencias instaladas:** Ninguna fue instalada; las dependencias están declaradas en `requirements.txt` pero no ejecutadas en el entorno de verificación.

- **Dependencias que NO pediste pero la IA agregó:**
  - `uvicorn[standard]==0.24.0` — servidor ASGI usado para ejecutar aplicaciones FastAPI. Aunque es útil para correr la API, no fue solicitado explícitamente en el prompt original.
  - `pydantic==2.5.0` — usado para validación y definición de modelos de datos. FastAPI lo utiliza comúnmente, pero no fue pedido directamente.
  - `python-multipart==0.0.6` — dependencia usada normalmente para manejo de formularios o carga de archivos. No fue solicitada y no parece necesaria para los endpoints básicos de préstamos de libros descritos en el prompt.

- **Archivos que NO pediste pero la IA generó:**
    - `.env.example` — archivo de ejemplo para variables de entorno. No fue solicitado en el prompt.
  - `.gitignore` — archivo para excluir elementos del control de versiones. No fue solicitado explícitamente.
  - `ARQUITECTURA.md` — documentación de la arquitectura del proyecto. No fue pedida.
  - `EJEMPLOS.md` — documentación con ejemplos de uso. No fue pedida.
  - `README.md` — documentación general del proyecto. No fue solicitada explícitamente.
  - `requests.http` — archivo para probar endpoints HTTP. No fue solicitado.
  - `requirements.txt` — archivo de dependencias. Es útil para el proyecto, pero no fue pedido directamente.
  - `run.bat` — script de ejecución para Windows. No fue solicitado.
  - `run.sh` — script de ejecución para Linux/macOS. No fue solicitado.

---

### Mapeo de reglas a código

### Mapeo de reglas a código

| Regla | Archivo y línea aproximada | ¿Aplica correctamente? | Notas |
|---|---:|---|---|
| RN1 — Límite de préstamos por tipo de estudiante | `main.py:L290` Linea 350 | No | El endpoint `POST /prestamos` no valida si el estudiante es de pregrado o posgrado, tampoco cuenta préstamos activos por estudiante ni retorna `409 Conflict` con `limite_prestamos_alcanzado`, además, el modelo `Estudiante` no tiene campo de tipo de estudiante, solo `carrera` |
| RN2 — Bloqueo por préstamo vencido | `main.py` lineas 290-350, `main.py` Linea 230-244 | No | No se valida en `POST /prestamos` si el estudiante tiene préstamos activos vencidos. Existe una lógica que marca préstamos como vencidos dentro de `obtener_prestamos_vigentes`, pero solo se ejecuta al consultar préstamos vigentes, no al crear un nuevo préstamo. |
| RN3 — Bloqueo por multas pendientes | No implementado | No | No existe modelo, lista en memoria ni validación relacionada con multas. Tampoco se retorna `409 Conflict` con `multa_pendiente`. |
| RN4 — Disponibilidad del ejemplar | `main.py:L321-L326`, `main.py:L188-L193`, `main.py:L343-L344` | Parcial | El sistema valida disponibilidad usando `cantidad_disponible` del libro y decrementa la cantidad al crear el préstamo. Sin embargo, la regla habla de un ejemplar con `estado = "disponible"`, y el código no maneja ejemplares individuales ni cambia estado a `prestado`. Además, retorna `400 Bad Request`, no `409 Conflict`. |
| RN5 — Duración del préstamo según tipo de libro | `main.py:L44-L47`, `main.py:L206-L210`, `main.py:L337-L340` | No | El plazo del préstamo se recibe desde el request mediante `dias_prestamo`, con valor por defecto de 14 días. No existe el atributo `alta_demanda` en los libros ni se calcula automáticamente el plazo de 3 o 15 días. |
| RN6 — Devolución de préstamo | `main.py:L246-L258`, `main.py:L392-L423` | Parcial | El sistema permite registrar la devolución, asigna `fecha_devolucion`, cambia el estado a `devuelto` e incrementa la disponibilidad del libro. Sin embargo, el endpoint implementado es `/prestamos/{prestamo_id}/devolver`, no `/prestamos/{id}/devolucion`. No calcula multa por retraso y, si el préstamo ya fue devuelto, retorna `400 Bad Request`, no `409 Conflict` con `prestamo_no_devolvible`. |
| RN7 — Cálculo de multa por devolución tardía | `main.py:L246-L258` | No | La devolución solo registra fecha y cambia el estado a `devuelto`. No compara `fecha_devolucion_real` contra `fecha_devolucion_esperada`, no calcula días de retraso, no multiplica por `2000` y no crea multas pendientes. |
| RN8 — Renovación de préstamo | No implementado | No | No existe endpoint `/prestamos/{id}/renovacion`. Tampoco hay campo `renovaciones`, validación de préstamo vencido para renovar ni control de solicitudes activas de otros estudiantes. |
| RN9 — Consulta de préstamos vencidos | `main.py:L230-L244`, `main.py:L354-L389` | Parcial | No existe endpoint `GET /prestamos/vencidos`. Hay lógica parcial en `obtener_prestamos_vigentes`, donde se marca un préstamo activo como vencido si la fecha de vencimiento ya pasó. Sin embargo, esa información se retorna mezclada dentro de `/prestamos/vigentes`, no en una ruta específica para vencidos. |
| RN10 — Historial de préstamos por estudiante | No implementado | No | No existe endpoint `GET /estudiantes/{codigo}/historial`. Tampoco hay búsqueda de préstamos por estudiante ni manejo del error `estudiante_no_encontrado` con el formato indicado. |

---

### Hallazgos detectados

#### Hallazgo H1

- **Archivo:** `main.py:37-47`, `main.py:290-350`
- **Tipo:** omisión de regla de negocio
- **Severidad:** alta
- **Regla violada:** RN1
- **Descripción:** No se valida el límite de préstamos por tipo de estudiante. El estudiante no tiene campo para identificar si es pregrado o posgrado.
- **Cómo lo detecté:** lectura humana del código.
- **Reproducción:**
  1. Ejecutar la API.
  2. Crear más de 3 préstamos para el mismo estudiante.
  3. Verificar que el sistema los permite mientras haya libros disponibles.

---

#### Hallazgo H2

- **Archivo:** `main.py:230-244`, `main.py:290-350`
- **Tipo:** omisión de validación
- **Severidad:** alta
- **Regla violada:** RN2
- **Descripción:** No se bloquea la creación de préstamos cuando el estudiante tiene préstamos vencidos.
- **Cómo lo detecté:** revisión del flujo de `POST /prestamos`.
- **Reproducción:**
  1. Crear un préstamo.
  2. Simular que la fecha de vencimiento ya pasó.
  3. Crear otro préstamo para el mismo estudiante.
  4. Verificar que no retorna `409 Conflict`.

---

#### Hallazgo H3

- **Archivo:** `main.py:16-22`, `main.py:188-198`, `main.py:321-326`
- **Tipo:** implementación parcial
- **Severidad:** media
- **Regla violada:** RN4
- **Descripción:** La disponibilidad se maneja por cantidad de libros, no por estado de ejemplar individual.
- **Cómo lo detecté:** revisión del modelo `Libro` y de la validación de disponibilidad.
- **Reproducción:**
  1. Crear préstamos hasta agotar un libro.
  2. Intentar crear otro préstamo del mismo libro.
  3. Verificar que retorna `400 Bad Request`, no `409 Conflict`.

---

#### Hallazgo H4

- **Archivo:** `main.py:44-47`, `main.py:206-224`, `main.py:337-340`
- **Tipo:** omisión de regla de negocio
- **Severidad:** alta
- **Regla violada:** RN5
- **Descripción:** La duración del préstamo la envía el usuario mediante `dias_prestamo`; no se calcula según `alta_demanda`.
- **Cómo lo detecté:** lectura humana del modelo `CrearPrestamo` y del método `crear_prestamo`.
- **Reproducción:**
  1. Enviar `POST /prestamos` con `dias_prestamo: 99`.
  2. Verificar que el sistema acepta ese valor.
  3. Confirmar que no calcula 3 o 15 días automáticamente.

---

#### Hallazgo H5

- **Archivo:** `main.py:246-258`, `main.py:392-423`
- **Tipo:** implementación parcial
- **Severidad:** alta
- **Regla violada:** RN6 y RN7
- **Descripción:** La devolución cambia el estado a `devuelto`, pero no calcula multas por retraso.
- **Cómo lo detecté:** revisión del método `registrar_devolucion`.
- **Reproducción:**
  1. Crear un préstamo vencido.
  2. Registrar la devolución.
  3. Verificar que no se genera multa pendiente.
  4. Intentar devolverlo de nuevo y observar que retorna `400`, no `409`.

---

#### Hallazgo H6

- **Archivo:** `main.py:274-286`, `main.py:290-350`, `main.py:354-389`, `main.py:392-423`
- **Tipo:** omisión de endpoints
- **Severidad:** alta
- **Regla violada:** RN8, RN9 y RN10
- **Descripción:** No existen endpoints para renovación, préstamos vencidos ni historial por estudiante.
- **Cómo lo detecté:** revisión de las rutas declaradas en FastAPI.
- **Reproducción:**
  1. Ejecutar la API.
  2. Probar `POST /prestamos/1/renovacion`.
  3. Probar `GET /prestamos/vencidos`.
  4. Probar `GET /estudiantes/1/historial`.
  5. Verificar que las rutas responden `404 Not Found`.

---

## Sección 2 — Resultados de los tests (Etapa 4)

### Primera ejecución

- **Tests totales:** 0
- **Pasaron:** 0
- **Fallaron:** 0

**Nota:** En la versión 1 no se encontraron tests automatizados. El proyecto incluye ejemplos de prueba manual con `curl`, Swagger UI, REST Client y Postman, pero no contiene archivos de prueba ni una suite ejecutable con `pytest`.

### Análisis de los fallos

| Test | Tipo de fallo | ¿Bug del código o test mal escrito? | Acción tomada |
|---|---|---|---|
| No aplica | No se ejecutaron tests automatizados | No aplica | Se realizó auditoría humana del código y se documentaron hallazgos H1-H6. |

### Última ejecución (post-correcciones)

- **Tests totales:** 0
- **Pasaron:** 0
- **Fallaron:** 0

**Nota:** No hubo una última ejecución de tests porque no se crearon ni ejecutaron pruebas automatizadas en esta versión.

### Tests rojos declarados (bugs no corregidos por tiempo)

No hubo tests rojos, porque no existía una suite de pruebas automatizadas. Sin embargo, quedaron documentados como bugs pendientes los siguientes hallazgos:
- **H1:** No se valida el límite de préstamos por tipo de estudiante.
- **H2:** No se bloquean nuevos préstamos cuando el estudiante tiene préstamos vencidos.
- **H3:** La disponibilidad se maneja por cantidad de libros, no por ejemplar individual.
- **H4:** La duración del préstamo no se calcula según si el libro es de alta demanda.
- **H5:** La devolución no calcula multas por retraso.
- **H6:** Faltan endpoints para renovación, préstamos vencidos e historial por estudiante.

## Sección Pruebas de reglas de negocio

- ¿Que codigo HTTP devolvio tu version sin IA?

- ¿Cual de las dos incluye un mensaje de error legible?
  En la version 1 que es con un prompt debil
- ¿El cuerpo de la respuesta identifica por que fallo?

## Preguntas de reflexion


1. ¿Cuantas reglas de negocio implemento correctamente tu version sin IA?

2. ¿Hubo alguna prueba donde la version sin IA devolvio `200 OK` cuando debia devolver `409` o `404`? ¿Que implica eso para un cliente que consume la API?

3. ¿Hay alguna regla de negocio que **ninguna** de las dos versiones implemento? Si es asi, ¿como lo detectaste?

4. Para las pruebas RN3, RN4 y RN7: si no pudiste ejecutarlas porque tu API no permite manipular fechas ni tiene lista de espera, ¿que dice eso sobre la completitud del sistema? ¿Deberia la especificacion haber contemplado esto?


---

## Sección 3 — Bugs corregidos (Etapa 5)

### Bug B1

- **Hallazgo asociado:** H1 (de la sección 1)
- **Descripción del bug:** [...]
- **Test que lo reveló:** [nombre del test]
- **Corrección aplicada:** [resumen de la corrección]
- **Tipo de corrección:** [por mí a mano / por IA con prompt acotado / mixta]
- **Resultado:** test ahora pasa. Sin regresiones.

### Bug B2

[Repite]

---

## Sección 4 — Aprendizajes (mínimo 3)

### Aprendizaje A1

[Una observación honesta de algo que descubriste hoy. No respondas lo políticamente correcto. Sé específico.]

**Ejemplo bueno:**

> "La IA generó código que parecía manejar correctamente las fechas, pero al ejecutar los tests descubrí que estaba comparando strings ISO directamente con `<` y `>`, lo cual funciona por accidente con fechas del mismo año pero rompe en otros casos. Aprendí que la IA confía en heurísticas que pueden ser frágiles."

**Ejemplo malo:**

> "Aprendí que la IA es útil pero hay que revisarla."

### Aprendizaje A2

### Aprendizaje A3

[Mínimo 3. Si tienes más, mejor.]

---

## Sección 5 — Decisiones de prompt (autorreflexión)

¿Hubo algún prompt que reescribiste a mitad de la sesión? Por ejemplo, primero le pediste a la IA "genera tests" y luego cambiaste a "genera tests anclados a las reglas de negocio sin mirar el código". Si pasó algo así, descríbelo.

[Tu respuesta]

¿Hubo algún momento en que la IA "dijo que terminó" pero al verificar tú descubriste que no? Descríbelo.

[Tu respuesta]
