# Registro de Prompt — #01

## Prompt #01

**Fecha y hora:** 2026-05-20 04:30 (aprox.)

**Propósito en una línea:** Definir el stack tecnológico, leer la especificación existente y generar la propuesta de árbol de directorios para la Versión 2 del sistema de biblioteca.

**Etapa del taller:** Etapa 2 — Generación del proyecto con IA

**IA usada:** Claude (Anthropic) — Cowork mode

---

### Prompt enviado (literal)

```
Actúa como un desarrollador Senior especializado en Python. Tu objetivo es inicializar la Versión 2 de nuestro sistema basándote estrictamente en la documentación existente.
1. Contexto y Lectura Obligatoria
Antes de generar cualquier línea de código, debes leer y analizar el archivo de especificaciones ubicado en: `C:\Users\matem\brief-biblioteca-ucaldas-1\02-tu-trabajo\plantilla-especificacion.md`
2. Restricciones Técnicas
El proyecto se desarrollará exclusivamente en la carpeta: `C:\Users\matem\brief-biblioteca-ucaldas-1\Version_2`

* Stack: Python + FastAPI.
* Persistencia: Solo datos en memoria (listas/diccionarios). No implementes bases de datos (SQL/NoSQL).
* Seguridad: Sin autenticación ni autorización para esta fase.
* Interfaz: Solo API REST (sin frontend).
* Testing: Suite de pruebas con `pytest`.
3. Reglas de Ejecución

1. Fidelidad: No inventes funcionalidades; cíñete al archivo `.md` leído.
2. Orden de Configuración: Antes de la lógica de negocio, genera los archivos base: `.gitignore`, `README.md`, `requirements.txt` y `.env` (si aplica).
3. Claridad: Si encuentras ambigüedades en la especificación, detente y pregunta antes de asumir una implementación.
4. Estructura: Propón una arquitectura de carpetas limpia (Clean Architecture).
4. Primera Tarea
Basado en lo anterior, genera una propuesta de árbol de directorios para la carpeta `Version_2`.
Espera mi aprobación del árbol de archivos antes de proceder con cualquier escritura de código
```

---

### Resumen de la respuesta de la IA

La IA leyó cuatro archivos de contexto antes de responder: `plantilla-especificacion.md`, `brief-cliente.md`, `taller-analisis-v1-v2.md` y `pruebas-reglas-negocio.md`. Detectó que `plantilla-especificacion.md` era una plantilla sin completar, pero extrajo las reglas de negocio concretas de `brief-cliente.md` y `pruebas-reglas-negocio.md`.

**Decisiones que la IA tomó sin que se las pidiera explícitamente:**

- Propuso una arquitectura de cuatro capas (Domain / Application / Infrastructure / API) basada en Clean Architecture, cuando el prompt solo decía "arquitectura de carpetas limpia". La interpretación concreta fue decisión propia de la IA.
- Identificó la entidad `Reserva` (lista de espera) y la incluyó en el árbol, aunque el correo de Diana Restrepo la menciona solo implícitamente (RN7: renovación bloqueada si hay estudiante esperando).
- Decidió separar `ILibroRepository` e `IEjemplarRepository` en el mismo archivo `libro_repository.py` por cohesión, sin que se le indicara esa agrupación.
- Planteó una pregunta sobre la lista de espera (Opción A: `POST /api/reservas` vs. Opción B: gestión interna) antes de proceder — esto sí estaba dentro de las reglas del prompt ("detente y pregunta si hay ambigüedades").

La IA admitió explícitamente que la especificación estaba incompleta (campos `[...]` sin llenar) y documentó su fuente de información alternativa.

---

### Mi evaluación

**¿La respuesta cumplió con lo que pedí?**

- [ ] Completamente.
- [x] Parcialmente. Faltó: [Mejorar la Arquitectura]
- [ ] No, se desvió. Hizo: [...]

**¿La acepté tal cual o la modifiqué?**

- [ ] Tal cual.
- [x] La modifiqué a mano. Cambios: [La arquitectura de las carpetas]
- [ ] Le pedí corrección con un prompt nuevo (ver prompt #[N+1]).
- [ ] La rechacé completamente. Razón: [...]

**¿Qué aprendí de esta interacción?**

[Una línea sobre qué te llevaste de este prompt. Por ejemplo:
> "La IA leyó más archivos de los que le pedí y extrajo contexto de todos ellos. La especificación incompleta no la bloqueó porque buscó información equivalente en otros archivos del proyecto."]
