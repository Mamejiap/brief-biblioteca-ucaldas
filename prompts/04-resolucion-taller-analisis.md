# Registro de Prompt — #04

## Prompt #04

**Fecha y hora:** 2026-05-20 06:14

**Propósito en una línea:** Resolver los ejercicios del taller de análisis comparativo v1-v2 usando exclusivamente la evidencia técnica de la Versión 2 implementada en Python/FastAPI.

**Etapa del taller:** Etapa 3 — Análisis crítico (Bloques 1, 2, 3 y 4 del taller)

**IA usada:** Claude (Anthropic) — Cowork mode

---

### Prompt enviado (literal)

```
Asunto: Resolución de Taller de Análisis - Enfoque en Versión 2
Actúa como un Auditor de Software y Analista Técnico. Tu objetivo es completar el taller de análisis comparativo basándote únicamente en el desarrollo de la Versión 2.
1. Insumos para el Análisis

* Documento Base: Lee `C:\Users\matem\brief-biblioteca-ucaldas-1\01-contexto\taller-analisis-v1-v2.md`.
* Evidencia Técnica: Analiza todo el código y la estructura implementada en la carpeta `C:\Users\matem\brief-biblioteca-ucaldas-1\Version_2`.
2. Instrucciones de Resolución

* Foco en V2: Resuelve todos los ejercicios, preguntas y cuadros comparativos del archivo `.md` utilizando la información de la Versión 2.
* Gestión de V1: Para cualquier sección, tabla o pregunta que pida información sobre la "Versión 1", déjala en blanco o marcada como "N/A", ya que nuestro análisis actual se centra exclusivamente en la evolución hacia la V2.
* Integridad: Está estrictamente prohibido modificar el archivo original en la carpeta `01-contexto`.
3. Salida y Documentación

1. Nuevo Archivo: Guarda los resultados en `C:\Users\matem\brief-biblioteca-ucaldas-1\02-tu-trabajo\taller_analisis_v2.md`.
2. Registro de Prompt: Crea el archivo de log correspondiente en `C:\Users\matem\brief-biblioteca-ucaldas-1\prompts` (ej. `04-resolucion-taller-analisis.md`), siguiendo la plantilla de registro que venimos utilizando.
Confirma cuando el taller haya sido procesado y el nuevo archivo esté disponible en la carpeta "02-tu-trabajo".
```

---

### Resumen de la respuesta de la IA

La IA leyó 7 archivos fuente antes de redactar: el taller (`taller-analisis-v1-v2.md`), más `crear_prestamo.py`, `estudiante.py`, `exceptions.py`, `test_crear_prestamo.py`, `error_handlers.py`, `schemas.py`, `test_prestamos_api.py` y `prestamo.py`. Generó el archivo `taller_analisis_v2.md` en `02-tu-trabajo/` y este registro de prompt.

**Estructura del análisis producido:**

- **Bloque 1, Ejercicio 1.1:** Tabla de 7 dimensiones comparativas, columna v1 en N/A, columna v2 completada con datos concretos del stack (Python, Pydantic v2, 4 capas, etc.).
- **Bloque 1, Ejercicio 1.2:** Rastreo de RN1 a través de las 3 capas que la implementan, con fragmentos de código y números de línea exactos. Respuesta a las 4 subpreguntas incluyendo la tabla de "archivos a modificar para cambiar el límite de pregrado" (respuesta: 1 archivo).
- **Bloque 2, Ejercicio 2.1:** Análisis del comportamiento ante request inválido, diferenciando respuesta `422` (body malformado) de respuesta `404` (IDs inexistentes). Muestra el JSON exacto que devolvería la API en cada caso.
- **Bloque 2, Ejercicio 2.2:** Tabla comparativa del error de "ejemplar ya prestado" con evidencia del código fuente (`exceptions.py` + `error_handlers.py`).
- **Bloque 3, Ejercicio 3.1:** Identificación de la técnica de aislamiento (fakes, no mocks), explicación de por qué no se levanta HTTP, mapeo de líneas donde se prueban RN3 y RN4, estimación del tiempo de ejecución con justificación.
- **Bloque 4, Ejercicio 4.1:** El test ya existía en el proyecto (`TestRN2Posgrado::test_sexto_prestamo_lanza_excepcion`). La IA lo reprodujo con comentarios explicativos y respondió la reflexión sobre por qué sería más lento en v1.

**Decisiones que la IA tomó sin que se las pidiera explícitamente:**

- Añadió una sección de **"Reflexión final"** que no estaba en el taller original, sintetizando la respuesta a la pregunta central del taller ("¿qué impacto tiene la estructura sobre la testabilidad?"). No fue solicitada.
- Para el Ejercicio 2.1, detectó que el comando `curl` del taller usa **camelCase** (`estudianteId`, `ejemplarId`) pero la API v2 usa **snake_case** (`estudiante_id`, `ejemplar_id`). Analizó ambos casos (body camelCase → `422`; body snake_case con IDs inexistentes → `404`) en lugar de responder solo uno. Esta distinción no se pedía explícitamente.
- Para el Ejercicio 3.1, pregunta 4 ("¿cuánto tiempo tarda en ejecutarse?"), la IA no pudo ejecutar pytest por falta de dependencias, pero estimó el tiempo con justificación técnica (~100ms unitarios, ~500ms-2s integración) en lugar de dejar la pregunta sin responder.
- Incluyó fragmentos de código con números de línea reales tomados de los archivos fuente para respaldar cada respuesta, lo cual va más allá del nivel de detalle que el enunciado pedía.

**Limitación admitida:** No fue posible completar la parte de "Corre `npm...`" del Ejercicio 3.1 (la línea del taller está truncada en el original) ni obtener tiempos reales de ejecución de pytest. Ambas limitaciones se documentaron en el archivo.

---

### Mi evaluación

**¿La respuesta cumplió con lo que pedí?**

- [ ] Completamente.
- [ ] Parcialmente. Faltó: [...]
- [ ] No, se desvió. Hizo: [...]

**¿La acepté tal cual o la modifiqué?**

- [ ] Tal cual.
- [ ] La modifiqué a mano. Cambios: [...]
- [ ] Le pedí corrección con un prompt nuevo (ver prompt #[N+1]).
- [ ] La rechacé completamente. Razón: [...]

**¿Qué aprendí de esta interacción?**

[Una línea sobre qué te llevaste de este prompt. Por ejemplo:
> "La IA detectó una inconsistencia entre el comando curl del taller (camelCase) y la API implementada (snake_case) que yo no había notado. Eso me indica que el taller fue escrito pensando en una convención diferente."]
