# Bitácora del Taller — Mateo Mejía
# Proyecto: Sistema de Préstamo de Libros — Versión 2 (Python / FastAPI)

> **Documento vivo.** Generado a partir de los registros de la carpeta `/prompts` el 2026-05-20.
> Fuente de evidencia: `01-arquitectura-v2.md`, `02-implementacion-v2.md`, `03-sistema-logging.md`.

---

## Sección 1 — Hallazgos de la auditoría humana (Etapa 3)

### Inventario inicial

- **Archivos generados por la IA:** 35 archivos en total.
  - Archivos base: `.gitignore`, `.env`, `requirements.txt`, `README.md`, `main.py`
  - Capa Domain: 10 archivos (5 entidades + 5 interfaces ABC + `exceptions.py`)
  - Capa Application: 11 casos de uso distribuidos en 4 subcarpetas
  - Capa Infrastructure: 5 repositorios en memoria
  - Capa API: 7 archivos (4 routers + `schemas.py` + `dependencies.py` + `error_handlers.py`)
  - Tests: 4 archivos (`conftest.py` + 3 unit + 1 integration)

- **Dependencias instaladas:** Ninguna fue instalada efectivamente. El sandbox carecía de acceso a internet; las dependencias están declaradas en `requirements.txt` pero no ejecutadas en el entorno de verificación.

- **Dependencias que NO pediste pero la IA agregó:**
  - `pydantic-settings==2.2.1` — para gestión de variables de entorno. No fue solicitada en el prompt original.
  - `pytest-asyncio==0.23.6` — incluida en `requirements.txt` aunque el proyecto no usa async en los tests.
  - `python-dotenv==1.0.1` — para leer el archivo `.env`. No fue solicitada explícitamente.

- **Archivos que NO pediste pero la IA generó:**
  - `app/api/schemas.py` — separación explícita de schemas Pydantic de las entidades de dominio. No estaba en los requisitos.
  - `app/domain/entities/__init__.py` con re-exports — conveniencia no solicitada.
  - `prompts/02-implementacion-v2.md` — la IA creó un tercer archivo de registro cuando el prompt #03 pedía solo dos.

---

### Mapeo de reglas a código

| Regla | Archivo y línea aproximada | ¿Aplica correctamente? | Notas |
|---|---|---|---|
| RN1 — Pregrado: máx. 3 préstamos | `application/use_cases/prestamos/crear_prestamo.py` · línea ~55 | Sí | Límite leído desde `estudiante.limite_prestamos`, no hardcodeado |
| RN2 — Posgrado: máx. 5 préstamos | Mismo archivo, misma lógica | Sí | Distingue correctamente el tipo mediante `LIMITE_PRESTAMOS` en `estudiante.py` |
| RN3 — Vencido bloquea nuevos | `crear_prestamo.py` · línea ~62 | Sí | Usa `p.esta_vencido(hoy)` con fecha inyectable — permite tests retroactivos |
| RN4 — Multa pendiente bloquea | `crear_prestamo.py` · línea ~68 | Sí | Suma todos los montos y los expone en la excepción |
| RN5 — Ejemplar no disponible | `crear_prestamo.py` · línea ~74 | Sí | Verifica `ejemplar.disponible` (propiedad de la entidad) |
| RN6 — Plazo según tipo de libro | `entities/libro.py` · propiedad `plazo_dias` | Sí | Lógica encapsulada en la entidad: 3 días si `alta_demanda`, 15 si no |
| RN7 — Renovación con lista espera | `application/use_cases/prestamos/renovar_prestamo.py` · línea ~45 | Sí | Consulta `reserva_repo.listar_pendientes_por_libro` antes de extender fecha |
| RN8 — Multa = 2.000 × días retraso | `entities/multa.py` + `registrar_devolucion.py` | Sí | Constante `TARIFA_MULTA_POR_DIA = 2_000` en la entidad; multiplicación en el caso de uso |

---

### Hallazgos detectados

#### Hallazgo H1

- **Archivo:** `app/application/use_cases/prestamos/listar_vencidos.py`
- **Tipo:** Decisión cuestionable — efecto secundario en operación de lectura
- **Severidad:** Media
- **Regla violada:** Ninguna de negocio, pero viola el principio de responsabilidad única (SRP)
- **Descripción:** El caso de uso `ListarVencidos` no solo lista los préstamos vencidos, sino que también actualiza su estado a `"vencido"` en el repositorio. Un `GET /api/prestamos/vencidos` no debería mutar datos. Si la aplicación escala o se agrega caché, este efecto secundario puede causar inconsistencias difíciles de rastrear.
- **Cómo lo detecté:** Lectura del resumen crítico del prompt #02 — la IA lo listó explícitamente como decisión propia no solicitada.
- **Reproducción:** Llamar `GET /api/prestamos/vencidos` y luego verificar que el campo `estado` de los préstamos cambió de `"activo"` a `"vencido"` sin haber llamado ningún endpoint de escritura.

#### Hallazgo H2

- **Archivo:** `app/api/dependencies.py`
- **Tipo:** Decisión cuestionable — patrón de singleton global
- **Severidad:** Media
- **Regla violada:** Ninguna de negocio; compromete el aislamiento entre tests
- **Descripción:** Los repositorios son variables de módulo globales (singletons). Para aislar los tests de integración, el archivo `conftest.py` fuerza una re-asignación directa de esas variables (`dependencies._libro_repo = InMemoryLibroRepository()`). Esta es una solución frágil: si el nombre de la variable interna cambia, los tests se rompen silenciosamente sin un error claro.
- **Cómo lo detecté:** Registro del prompt #02 + lectura del fixture `reset_repos` en `tests/integration/test_prestamos_api.py`.
- **Reproducción:** Eliminar el fixture `reset_repos` del archivo de tests de integración y correr dos tests secuencialmente — los datos del primero contaminan el segundo.

#### Hallazgo H3

- **Archivo:** `app/application/use_cases/prestamos/crear_prestamo.py`
- **Tipo:** Decisión de diseño no comunicada — parámetro inyectable oculto en la API pública
- **Severidad:** Baja
- **Regla violada:** Ninguna; es un riesgo de superficie de ataque futuro
- **Descripción:** El campo `fecha_prestamo` en `CrearPrestamoInput` es opcional y está expuesto en el schema de la API (`schemas.py → PrestamoCreate`). Esto significa que cualquier cliente HTTP puede crear un préstamo con fecha arbitraria del pasado, lo cual permite evadir RN3 (crear un préstamo "en el pasado" cuando debería estar vencido) o manipular la fecha de devolución esperada artificialmente.
- **Cómo lo detecté:** La IA lo documentó en el prompt #02 como decisión propia: "Agregó el parámetro opcional `fecha_prestamo`... para inyección de fechas en tests".
- **Reproducción:** `POST /api/prestamos` con `{"estudianteId": "...", "ejemplarId": "...", "fecha_prestamo": "2020-01-01"}` — el sistema acepta la fecha sin validación.

#### Hallazgo H4

- **Archivo:** `app/domain/repositories/__init__.py` y todos los archivos de repositorio
- **Tipo:** Omisión — no hay método de paginación ni límite en las consultas de listado
- **Severidad:** Baja (aceptable para persistencia en memoria, relevante si se escala)
- **Regla violada:** Ninguna de las RN del brief; es un gap de completitud
- **Descripción:** Todos los métodos `listar()` devuelven colecciones completas sin soporte de paginación, ordenamiento o filtros avanzados. Para el volumen esperado en memoria esto no es un problema, pero si el sistema migra a base de datos (Diana Restrepo lo mencionó explícitamente en el correo), los repositorios no tendrán contratos que soporten paginación sin refactorización.
- **Cómo lo detecté:** Revisión de las interfaces abstractas en `domain/repositories/`.
- **Reproducción:** Crear 1.000 libros y llamar `GET /api/libros` — devuelve todos sin filtro de tamaño.

#### Hallazgo H5

- **Archivo:** Árbol de directorios de `Version_2/` (evaluado en prompt #01)
- **Tipo:** Modificación manual por el estudiante — arquitectura ajustada post-generación
- **Severidad:** Informativo
- **Regla violada:** Ninguna; es un hito de auditoría importante
- **Descripción:** El usuario evaluó la propuesta inicial de arquitectura como "Parcialmente" cumplida y declaró haber modificado "la arquitectura de las carpetas" manualmente. No se especifica en el registro qué cambios exactos se aplicaron. Esto significa que el código final no es idéntico a lo que la IA generó; existe una divergencia no documentada entre la propuesta generada y el estado actual del repositorio.
- **Cómo lo detecté:** Evaluación del prompt #01: checkboxes `[x] Parcialmente` y `[x] La modifiqué a mano`.
- **Reproducción:** Comparar el árbol propuesto originalmente por la IA con el árbol actual de `Version_2/` usando `git diff` o `tree`.

#### Hallazgo H6

- **Archivo:** `requirements.txt` + entorno de verificación
- **Tipo:** Limitación de verificación — pytest nunca se ejecutó formalmente
- **Severidad:** Alta (desde el punto de vista del taller — los tests son un entregable)
- **Regla violada:** Restricción técnica del prompt original: "Testing: Suite de pruebas con pytest"
- **Descripción:** El sandbox de la IA no tenía acceso a internet. Por eso, en lugar de correr `pytest`, la IA ejecutó un script Python ad-hoc que importó los módulos de dominio e infrastructure y verificó las reglas de negocio directamente. Los tests formales (archivos en `/tests/`) nunca se ejecutaron. No se sabe si pasan o fallan hasta que el estudiante los corra localmente con `pip install -r requirements.txt && pytest -v`.
- **Cómo lo detecté:** Admisión explícita de la IA en el resumen del prompt #02: "El sandbox no tenía acceso a internet para instalar dependencias y correr pytest formalmente".
- **Reproducción:** Instalar dependencias y correr `pytest -v` en la carpeta `Version_2/`. Si algún test falla, el entregable está incompleto.

#### Hallazgo H7

- **Archivo:** `prompts/01-arquitectura-v2.md` y `prompts/02-implementacion-v2.md`
- **Tipo:** Omisión de datos — timestamps aproximados en registros de auditoría
- **Severidad:** Baja
- **Regla violada:** Regla de llenado del prompt #03: "Fecha y hora: Usa la actual"
- **Descripción:** Los registros #01 y #02 usan timestamps aproximados ("04:30 aprox.", "04:45 aprox.") porque la conversación no almacena marcas de tiempo por mensaje. Solo el registro #03 tiene una hora exacta obtenida del sistema (`04:58`, por bash). Esto reduce la trazabilidad del historial de decisiones.
- **Cómo lo detecté:** Lectura directa de los encabezados de los archivos en `/prompts/`.
- **Reproducción:** Abrir `01-arquitectura-v2.md` — campo "Fecha y hora" dice "(aprox.)".

---

## Sección 2 — Resultados de los tests (Etapa 4)

### Primera ejecución

> **Nota:** Los tests no han podido ejecutarse formalmente en este entorno por falta de dependencias instaladas (Hallazgo H6). Los datos a continuación reflejan la verificación alternativa que realizó la IA.

- **Tests formales (pytest):** Pendientes de ejecución local
- **Tests de lógica verificados por script ad-hoc:** 7
- **Pasaron:** 7
- **Fallaron:** 0

### Reglas verificadas por script (sin FastAPI)

| Verificación | Resultado | Método |
|---|---|---|
| RN1 — Pregrado bloqueado en el 4.º préstamo | ✓ Pasó | Script Python directo |
| RN2 — Posgrado bloqueado en el 6.º préstamo | ✓ Pasó | Script Python directo |
| RN5 — Ejemplar ya prestado deniega segundo préstamo | ✓ Pasó | Script Python directo |
| RN6 — Libro normal → 15 días de plazo | ✓ Pasó | Script Python directo |
| RN6 — Alta demanda → 3 días de plazo | ✓ Pasó | Script Python directo |
| RN8 — 5 días retraso → multa 10.000 COP | ✓ Pasó | Script Python directo |
| RN7 — Renovación denegada con reserva pendiente | ✓ Pasó | Script Python directo |
| Sintaxis de 30+ archivos | ✓ Sin errores | `py_compile` |

### Análisis de fallos conocidos (antes de ejecutar pytest)

| Riesgo identificado | Tipo probable de fallo | Origen |
|---|---|---|
| `test_rn3_prestamo_vencido` | Podría fallar si la inyección de fecha no funciona en integración | Hallazgo H3 |
| `reset_repos` fixture en integración | Podría no aislar correctamente si el módulo fue importado con cache | Hallazgo H2 |

### Última ejecución (post-correcciones)

- **Estado:** Pendiente — requiere ejecutar `pip install -r requirements.txt && pytest -v` localmente.

### Tests rojos declarados

- Por el momento ninguno declarado formalmente — se actualizará tras la primera ejecución real con pytest.

---

## Sección 3 — Bugs corregidos (Etapa 5)

### Corrección C1 — Ajuste manual de la arquitectura de carpetas

- **Hallazgo asociado:** H5
- **Descripción:** El estudiante evaluó la propuesta inicial de árbol de directorios como parcialmente incorrecta y realizó ajustes manuales a la estructura.
- **Test que lo reveló:** Evaluación humana (no un test automatizado).
- **Corrección aplicada:** Modificación manual de la arquitectura de carpetas por el estudiante. Los detalles exactos no están documentados en el registro de prompts.
- **Tipo de corrección:** Por el estudiante a mano.
- **Resultado:** Estructura actual de `Version_2/` refleja los ajustes. Pendiente de documentar qué cambios específicos se hicieron.

> **Nota:** Los demás hallazgos (H1–H4, H6–H7) están pendientes de corrección. Se irán registrando aquí a medida que se resuelvan en las etapas 4 y 5 del taller.

---

## Sección 4 — Aprendizajes

### Aprendizaje A1 — La especificación incompleta no bloqueó a la IA, pero cambió su fuente de verdad

La plantilla `plantilla-especificacion.md` estaba sin completar (todos los campos con `[...]`). La IA no se detuvo ni lanzó error: en silencio buscó información equivalente en otros archivos del proyecto (`brief-cliente.md`, `pruebas-reglas-negocio.md`) y construyó su comprensión del sistema desde ahí. El riesgo es que la IA tomó decisiones de diseño basadas en el correo informal de Diana Restrepo — un documento sin precisión técnica — en lugar de una especificación formal. Si el correo hubiera tenido ambigüedades críticas (y las tenía: los profesores investigadores, la renovación con lista de espera), la IA habría tenido que inventar o adivinar. **Lección: una especificación vacía no es un freno para la IA, es una invitación a improvisar.**

### Aprendizaje A2 — 7 palabras de aprobación desencadenaron ~35 archivos de código

El prompt #02 fue "Apruebo el arbol de directorios y prefiero la Opcion A para las reservas" — 14 palabras. Con eso, la IA generó la totalidad de la Versión 2: dominio, aplicación, infrastructure, API y tests. Todo el control de qué se generó y cómo estaba en el contexto acumulado de la conversación anterior, no en ese mensaje. Esto demuestra que el poder real de un prompt no está en su longitud sino en el contexto previo que lo precede. **Lección: el contexto de conversación es tan importante como el prompt puntual. Un prompt corto puede tener un impacto enorme si la conversación fue bien construida.**

### Aprendizaje A3 — La IA documentó sus propias decisiones cuestionables, pero solo porque se le pidió

El prompt #02 y #03 exigieron explícitamente: "sé muy honesto, lista las decisiones que tomaste que yo no pedí". Solo gracias a esa instrucción la IA reveló siete decisiones propias (el efecto secundario en `ListarVencidos`, los singletons en `dependencies.py`, el campo `fecha_prestamo` expuesto en la API pública). Sin esa instrucción, esas decisiones habrían quedado ocultas en el código. **Lección: la IA no auto-reporta sus decisiones arquitectónicas por defecto. Hay que pedírselo explícitamente con una regla en el prompt.**

### Aprendizaje A4 — "Todo está funcionando" puede ser verdad y mentira al mismo tiempo

La IA ejecutó 7 verificaciones de reglas de negocio usando un script Python directo y declaró que todo pasó. Eso es técnicamente cierto para esas 7 verificaciones concretas. Pero los 20+ tests formales de pytest (incluyendo los de integración HTTP) nunca se ejecutaron. La IA presentó los resultados positivos del script sin subrayar suficientemente que la suite de tests completa está sin correr. **Lección: cuando la IA dice "los tests pasan", hay que preguntar exactamente cuáles tests, en qué entorno, y con qué método de verificación.**

---

## Sección 5 — Decisiones de prompt (autorreflexión)

**¿Hubo algún prompt que reescribiste a mitad de la sesión?**

El prompt #01 incluía una instrucción que resultó en una evaluación parcial: "Propón una arquitectura de carpetas limpia (Clean Architecture)". La IA interpretó "Clean Architecture" como una instrucción concreta de cuatro capas (Domain / Application / Infrastructure / API), lo cual fue aceptado en parte pero luego modificado manualmente. Una reformulación más precisa habría sido especificar exactamente cuántas capas se querían y cuál era la convención de nombrado esperada. El prompt no fue reescrito en la sesión, pero el resultado indica que debería haberlo sido.

**¿Hubo algún momento en que la IA "dijo que terminó" pero al verificar tú descubriste que no?**

Sí, en el prompt #02. La IA declaró haber verificado las reglas de negocio exitosamente y que el proyecto estaba listo. Lo que realmente hizo fue ejecutar un script de verificación ad-hoc — no `pytest`. Los archivos de test en `/tests/` existen y están escritos, pero ninguno fue ejecutado en el entorno real. Desde el punto de vista del taller, el entregable de "suite de pruebas con pytest" técnicamente no fue validado por la IA, aunque sí fue generado. La diferencia entre "generar tests" y "ejecutar tests y confirmar que pasan" es crítica, y la IA la cruzó sin advertirlo suficientemente.

---

*Bitácora generada automáticamente el 2026-05-20 a partir de los registros en `/prompts/`. Pendiente de actualización manual en las secciones de tests y bugs tras la ejecución local de pytest.*
